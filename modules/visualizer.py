import plotly.express as px
import plotly.graph_objects as go #noqa
import pandas as pd #noqa

def plot_spread(df):
    df['spread'] = df['ask'] - df['bid']
    return px.line(df, x='timestamp', y='spread', title='Bid-Ask Spread Over Time')
# def plot_spread(df):
#     df['spread'] = df['ask'] - df['bid']
#     return px.line(df, x='timestamp', y='spread', title='Bid-Ask Spread Over Time')

def plot_volume(df):
    return px.line(df, x='timestamp', y='volume', title='Trading Volume Over Time')

def depth_heatmap(bids, asks):
    bids['side'] = 'bid'
    asks['side'] = 'ask'
    df = pd.concat([bids, asks])

    fig = px.density_heatmap(
        df, x="price", y="qty", z="qty",
        title="Order Book Depth Heatmap"
    )
    return fig
