import numpy as np
import pandas as pd #noqa

def bid_ask_spread(df):
    return (df['ask'] - df['bid']).mean()

# def amihud_illiquidity(df):
#     return np.mean(np.abs(df['returns']) / df['volume'])

def amihud_illiquidity(df):
    # If returns column is missing, compute it from close prices
    if 'returns' not in df.columns:
        if 'close' not in df.columns:
            raise ValueError("To compute Amihud Illiquidity, the dataset must contain either 'returns' or 'close'.")
        df['returns'] = df['close'].pct_change(fill_method=None)
        # df['returns'] = df['close'].pct_change()

    # Avoid division by zero or NaN issues
    valid = df[['returns', 'volume']].dropna()
    valid = valid[valid['volume'] > 0]

    if valid.empty:
        return np.nan

    return np.mean(np.abs(valid['returns']) / valid['volume'])

def order_book_imbalance(bids, asks):
    bid_vol = bids['qty'].sum()
    ask_vol = asks['qty'].sum()
    return (bid_vol - ask_vol) / (bid_vol + ask_vol)

def kyles_lambda(df):
    cov = np.cov(df['returns'], df['signed_volume'])[0,1]
    var = np.var(df['signed_volume'])
    return cov / var
