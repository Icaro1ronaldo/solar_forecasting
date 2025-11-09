from typing import Any, Dict, Optional, Tuple
import pandas as pd


def _ensure_datetime_index(
    df: pd.DataFrame, timestamp_col: Optional[str] = None
) -> pd.DataFrame:
    """
    Ensure the DataFrame has a DatetimeIndex.

    If timestamp_col is provided the column is converted to datetime and set as index.
    The returned DataFrame is a sorted copy.
    """
    if timestamp_col is not None:
        df2 = df.copy()
        df2.loc[:, timestamp_col] = pd.to_datetime(df2[timestamp_col])
        df2 = df2.set_index(timestamp_col)
    else:
        df2 = df.copy()
        if not isinstance(df2.index, pd.DatetimeIndex):
            df2.index = pd.to_datetime(df2.index)
    return df2.sort_index()


def _missing_timestamps(
    index: pd.DatetimeIndex, expected_freq: str
) -> Tuple[pd.DatetimeIndex, int]:
    """
    Compute missing timestamps relative to an expected frequency.

    Returns (missing_index, missing_count).
    """
    if index.empty:
        return pd.DatetimeIndex([]), 0
    full = pd.date_range(start=index.min(), end=index.max(), freq=expected_freq)
    missing = full.difference(index)
    return missing, len(missing)


def _longest_nan_run(
    series: pd.Series,
) -> Tuple[int, Optional[pd.Timestamp], Optional[pd.Timestamp]]:
    """
    Find the longest consecutive run of NaNs in a Series.

    Returns (length_in_samples, start_timestamp, end_timestamp).
    If no NaNs are present returns (0, None, None).
    """
    if series.isna().sum() == 0:
        return 0, None, None

    max_len = 0
    start_ts = None
    end_ts = None
    in_run = False
    run_start = None
    run_len = 0
    prev_ts = None

    for ts, val in series.items():
        if pd.isna(val):
            if not in_run:
                in_run = True
                run_start = ts
                run_len = 1
            else:
                run_len += 1
        else:
            if in_run:
                if run_len > max_len:
                    max_len = run_len
                    start_ts = run_start
                    end_ts = prev_ts
                in_run = False
                run_len = 0
        prev_ts = ts

    # handle run that reaches the end
    if in_run and run_len > max_len:
        max_len = run_len
        start_ts = run_start
        end_ts = prev_ts

    return int(max_len), start_ts, end_ts


def generate_completeness_report(
    df: pd.DataFrame,
    timestamp_col: Optional[str] = None,
    expected_freq: str = "15min",
    sample_missing_ts: int = 10,
) -> Dict[str, Any]:
    """
    Generate a completeness report for a time-series DataFrame.

    The report dictionary contains:
      - total_rows: number of rows present
      - expected_rows: number of expected rows given the index span and expected_freq
      - missing_timestamps_count, missing_timestamps_pct
      - sample_missing_timestamps: list of first missing timestamps as strings
      - duplicated_index_count: number of duplicated index entries
      - columns: per-column dict with missing_count, missing_pct, longest_nan_run_samples,
                 longest_nan_run_start, longest_nan_run_end, longest_nan_run_duration
    """
    df_dt = _ensure_datetime_index(df, timestamp_col=timestamp_col)

    total_rows = len(df_dt)
    missing_ts_index, missing_ts_count = _missing_timestamps(df_dt.index, expected_freq)
    expected_rows = (
        int(
            len(
                pd.date_range(
                    start=df_dt.index.min(), end=df_dt.index.max(), freq=expected_freq
                )
            )
        )
        if total_rows > 0
        else 0
    )
    missing_ts_pct = (
        (missing_ts_count / expected_rows * 100) if expected_rows > 0 else 0.0
    )

    duplicated_index_count = int(df_dt.index.duplicated().sum())

    columns_report: Dict[str, Dict[str, Any]] = {}
    for col in df_dt.columns:
        s = df_dt[col]
        missing_count = int(s.isna().sum())
        missing_pct = (missing_count / total_rows * 100) if total_rows > 0 else 0.0
        run_len, run_start, run_end = _longest_nan_run(s)
        # try to convert run length to duration based on expected_freq
        try:
            freq_td = pd.to_timedelta(expected_freq)
            longest_gap_duration = (
                (run_len * freq_td) if run_len > 0 else pd.Timedelta(0)
            )
        except Exception:
            longest_gap_duration = None

        columns_report[col] = {
            "missing_count": missing_count,
            "missing_pct": round(float(missing_pct), 4),
            "longest_nan_run_samples": run_len,
            "longest_nan_run_start": run_start,
            "longest_nan_run_end": run_end,
            "longest_nan_run_duration": longest_gap_duration,
        }

    report: Dict[str, Any] = {
        "total_rows": total_rows,
        "expected_rows": expected_rows,
        "missing_timestamps_count": missing_ts_count,
        "missing_timestamps_pct": round(float(missing_ts_pct), 4),
        "sample_missing_timestamps": list(
            missing_ts_index[:sample_missing_ts].astype(str)
        ),
        "duplicated_index_count": duplicated_index_count,
        "columns": columns_report,
    }
    return report


def print_completeness_report(report: Dict[str, Any]) -> None:
    """
    Pretty-print a human readable completeness report produced by generate_completeness_report.
    """
    print("=== Data Completeness Report ===")
    print(f"Total rows present: {report.get('total_rows')}")
    print(f"Expected rows (range/freq): {report.get('expected_rows')}")
    print(
        f"Missing timestamps: {report.get('missing_timestamps_count')} ({report.get('missing_timestamps_pct')}%)"
    )
    sample = report.get("sample_missing_timestamps", [])
    if sample:
        print(
            f"Sample missing timestamps (first {min(10, len(sample))}): {sample[:10]}"
        )
    print(f"Duplicated index entries: {report.get('duplicated_index_count')}")
    print("\nPer-column missingness:")
    for col, info in report.get("columns", {}).items():
        print(
            f" - {col}: {info['missing_count']} missing ({info['missing_pct']}%), "
            f"longest NaN run = {info['longest_nan_run_samples']} samples, "
            f"duration = {info['longest_nan_run_duration']}"
        )
