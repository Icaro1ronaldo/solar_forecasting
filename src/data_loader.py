
import pandas as pd

def load_data(filepath: str) -> pd.DataFrame:
    """
    Load interval data from a CSV file with selected columns and datetime index.

    Parameters:
    - filepath (str): Path to the CSV file.

    Returns:
    - pd.DataFrame: Preprocessed DataFrame with selected columns and datetime index.
    """
    selected_columns = [
        'Unnamed: 0',
        'actual power',
        'reference power',
        'poa irradiance (array tilt)',
        'ambient temperature',
        'ghi',
        'wind speed'
    ]

    df = pd.read_csv(
        filepath,
        usecols=selected_columns,
        index_col='Unnamed: 0',
        parse_dates=True
    )
    return df
