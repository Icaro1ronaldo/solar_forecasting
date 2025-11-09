import logging
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Schemas
DEFAULT_SCHEMA: Dict[str, str] = {
    "actual power": "float",
    "reference power": "float",
    "poa irradiance (array tilt)": "float",
    "ambient temperature": "float",
    "ghi": "float",
    "wind speed": "float",
}

POWER_SCHEMA: Dict[str, str] = {
    "actual power": "float",
    "reference power": "float",
}

METEO_SCHEMA: Dict[str, str] = {
    "poa irradiance (array tilt)": "float",
    "ambient temperature": "float",
    "ghi": "float",
    "wind speed": "float",
}


def _ensure_datetime_index(
    df: pd.DataFrame, timestamp_col: Optional[str] = None
) -> pd.DataFrame:
    """
    Ensure the DataFrame has a DatetimeIndex. If timestamp_col is provided and present,
    it will be converted to DatetimeIndex. Otherwise assumes index is datetime-like.
    """
    df = df.copy()
    if timestamp_col and timestamp_col in df.columns:
        df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")
        df = df.set_index(timestamp_col)
    else:
        # try to convert index
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            try:
                df.index = pd.to_datetime(df.index, errors="coerce")
            except Exception:
                pass
    return df


def check_columns(df: pd.DataFrame, required: List[str]) -> Dict[str, Any]:
    missing = [c for c in required if c not in df.columns]
    extra = [c for c in df.columns if c not in required]
    return {"missing_columns": missing, "extra_columns": extra}


def check_dtypes(df: pd.DataFrame, expected: Dict[str, str]) -> Dict[str, Any]:
    mismatches: Dict[str, Any] = {}
    for col, exp in expected.items():
        if col not in df.columns:
            mismatches[col] = {"status": "missing"}
            continue
        actual_dtype = str(df[col].dtype)
        if exp in ("float", "int"):
            ok = pd.api.types.is_numeric_dtype(df[col])
        elif exp == "datetime":
            ok = pd.api.types.is_datetime64_any_dtype(df[col])
        else:
            ok = actual_dtype.startswith(exp)
        if not ok:
            mismatches[col] = {"expected": exp, "actual": actual_dtype}
    return {"dtype_mismatches": mismatches}


def check_value_ranges(
    df: pd.DataFrame, ranges: Dict[str, Tuple[Optional[float], Optional[float]]]
) -> Dict[str, Any]:
    """Check whether values fall outside provided ranges. ranges: {col: (min, max)}"""
    issues: Dict[str, Any] = {}
    for col, (min_v, max_v) in ranges.items():
        if col not in df.columns:
            issues[col] = {"status": "missing"}
            continue
        s = df[col].dropna()
        if s.empty:
            issues[col] = {"status": "no_data"}
            continue
        out_of_range: Dict[str, int] = {}
        if min_v is not None:
            below = int((s < min_v).sum())
            if below:
                out_of_range["below_min"] = below
        if max_v is not None:
            above = int((s > max_v).sum())
            if above:
                out_of_range["above_max"] = above
        if out_of_range:
            issues[col] = out_of_range
    return {"range_issues": issues}


def check_duplicates(df: pd.DataFrame) -> Dict[str, Any]:
    dup_index = int(df.index.duplicated().sum())
    return {"duplicate_index_count": dup_index}


def check_timestamp_index(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Check index is datetime, timezone-aware, monotonic, and compute inferred frequency.
    """
    info: Dict[str, Any] = {}
    df = df.copy()
    info["index_is_datetime"] = pd.api.types.is_datetime64_any_dtype(df.index)
    if not info["index_is_datetime"]:
        info["note"] = "Index is not datetime"
        return info

    tz = getattr(df.index, "tz", None)
    info["tz"] = str(tz) if tz else None
    info["is_monotonic_increasing"] = df.index.is_monotonic_increasing
    info["inferred_freq"] = pd.infer_freq(df.index)
    return info


def check_frequency_and_gaps(
    df: pd.DataFrame, expected_freq: str = "15T"
) -> Dict[str, Any]:
    """
    Check the expected frequency and return count and examples of missing timestamps and misaligned ones.
    """
    df = _ensure_datetime_index(df)
    result: Dict[str, Any] = {"expected_freq": expected_freq}
    if df.index.empty:
        result.update({"n_missing": 0, "missing_examples": [], "n_misaligned": 0})
        return result

    try:
        full = pd.date_range(
            start=df.index.min(), end=df.index.max(), freq=expected_freq, tz=df.index.tz
        )
    except Exception:
        full = pd.date_range(
            start=df.index.min(), end=df.index.max(), freq=expected_freq
        )

    missing = full.difference(df.index.unique())
    result["n_missing"] = int(len(missing))
    result["missing_examples"] = list(map(str, missing[:10]))

    # misaligned timestamps (not exactly on expected grid)
    try:
        remainder = df.index.to_series().dt.floor(expected_freq) != df.index.to_series()
        result["n_misaligned"] = int(remainder.sum())
    except Exception:
        result["n_misaligned"] = 0

    return result


def _detect_df_type(df: pd.DataFrame) -> Optional[str]:
    """Auto-detect whether dataframe is 'power' or 'meteo' based on column presence."""
    cols = set(df.columns)
    if set(POWER_SCHEMA.keys()).issubset(cols):
        return "power"
    if set(METEO_SCHEMA.keys()).issubset(cols):
        return "meteo"
    return None


def generate_consistency_report(
    df: pd.DataFrame,
    schema: Optional[Dict[str, str]] = None,
    ranges: Optional[Dict[str, Tuple[Optional[float], Optional[float]]]] = None,
    timestamp_col: Optional[str] = None,
    expected_freq: str = "15T",
    df_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run a suite of consistency checks and return a report dict.
    """
    # choose schema: explicit > forced df_type > auto-detect > DEFAULT_SCHEMA
    if schema is None:
        chosen_type = df_type or _detect_df_type(df)
        if chosen_type == "power":
            schema_to_use = POWER_SCHEMA
            ranges = ranges or {
                "actual power": (0.0, None),
                "reference power": (0.0, None),
            }
        elif chosen_type == "meteo":
            schema_to_use = METEO_SCHEMA
            ranges = ranges or {
                "poa irradiance (array tilt)": (0.0, 2000.0),  # W/m^2
                "ghi": (0.0, 2000.0),  # W/m^2
                "ambient temperature": (-60.0, 60.0),  # °C
                "wind speed": (0.0, 60.0),  # m/s
            }
        else:
            schema_to_use = DEFAULT_SCHEMA
            ranges = ranges or {
                "poa irradiance (array tilt)": (0.0, 2000.0),
                "ghi": (0.0, 2000.0),
                "ambient temperature": (-60.0, 60.0),
                "wind speed": (0.0, 60.0),
                "actual power": (0.0, None),
                "reference power": (0.0, None),
            }
    else:
        schema_to_use = schema
        ranges = ranges or {}  # Évite None

    report: Dict[str, Any] = {}
    df_checked = _ensure_datetime_index(df, timestamp_col=timestamp_col)

    report["detected_type"] = df_type or _detect_df_type(df)
    report["schema_used"] = list(schema_to_use.keys())
    report["columns"] = check_columns(df_checked, list(schema_to_use.keys()))
    report["dtypes"] = check_dtypes(df_checked, schema_to_use)
    report["ranges"] = check_value_ranges(df_checked, ranges)
    report["duplicates"] = check_duplicates(df_checked)
    report["timestamp"] = check_timestamp_index(df_checked)
    report["frequency_and_gaps"] = check_frequency_and_gaps(
        df_checked, expected_freq=expected_freq
    )

    numeric = df_checked.select_dtypes(include=[np.number])
    report["numeric_summary"] = (
        numeric.describe().to_dict() if not numeric.empty else {}
    )

    return report  # Assurez-vous que la fonction retourne toujours un dictionnaire


def print_consistency_report(report: Dict[str, Any]) -> None:
    """Pretty-print a compact human-readable report."""
    print("=== Data Consistency Report ===")
    print(f"Detected/forced type: {report.get('detected_type')}")
    print(f"Schema used: {report.get('schema_used')}")
    print(f"Missing columns: {report['columns']['missing_columns']}")
    print(f"Extra columns: {report['columns']['extra_columns']}")
    print(f"Dtype mismatches: {len(report['dtypes']['dtype_mismatches'])}")
    print(f"Duplicate index rows: {report['duplicates']['duplicate_index_count']}, ")
    print(f"Timestamp info: {report['timestamp']}")
    freq = report.get("frequency_and_gaps", {})
    print(
        f"Frequency/gaps: missing={freq.get('n_missing')}, misaligned={freq.get('n_misaligned')}"
    )
    if report["ranges"].get("range_issues"):
        print("Range issues (first 5):")
        for i, (col, info) in enumerate(report["ranges"]["range_issues"].items()):
            print(f" - {col}: {info}")
            if i >= 4:
                break
