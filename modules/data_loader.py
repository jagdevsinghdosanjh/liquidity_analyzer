import pandas as pd

def load_csv(file):
    df = pd.read_csv(file)

    # Standardize column names
    df.columns = [c.lower().strip() for c in df.columns]

    # Compute returns if missing
    df = compute_returns(df)

    return df


def compute_returns(df):
    if 'returns' not in df.columns and 'close' in df.columns:
        df['returns'] = df['close'].pct_change()
    return df
