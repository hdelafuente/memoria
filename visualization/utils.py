# Visualization
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pandas import DataFrame


def plot_heatmap(corr_matrix):
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Heatmap(
            z=corr_matrix.values,
            x=[
                'Open',
                'Close',
                'n_very_bullish',
                'n_very_bearish',
                'n_bullish',
                'n_bearish',
                'n_neutral',
                'change_24hrs',
            ],
            y=[
                'Open',
                'Close',
                'n_very_bullish',
                'n_very_bearish',
                'n_bullish',
                'n_bearish',
                'n_neutral',
                'change_24hrs',
            ],
            type='heatmap',
            colorscale='Viridis',
        ),
        row=1,
        col=1,
    )
    print('Plotting heatmap...')
    fig.show()


def plot_results(dataframe: DataFrame, price_rep='candlestick'):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)
    if price_rep == 'bars':
        fig.add_trace(
            go.Bar(
                name='24h Variation',
                x=dataframe.index,
                y=dataframe.change_24hrs,
                offsetgroup=0,
            ),
            row=1,
            col=1,
        )
    elif price_rep == 'candlestick':
        fig.add_trace(
            go.Candlestick(
                x=dataframe.index,
                open=dataframe['Open'],
                high=dataframe['High'],
                low=dataframe['Low'],
                close=dataframe['Close'],
                name=f'Price BTC-USDT',
            ),
            row=1,
            col=1,
        )
    fig.add_trace(
        go.Bar(
            name='Very Bullish',
            x=dataframe.index,
            y=dataframe.n_very_bullish,
            offsetgroup=0,
            marker_color='green',
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            name='Bullish',
            x=dataframe.index,
            y=dataframe.n_bullish,
            offsetgroup=0,
            marker_color='lightgreen',
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            name='Bearish',
            x=dataframe.index,
            y=dataframe.n_bearish,
            offsetgroup=0,
            marker_color='orange',
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            name='Very Bearish',
            x=dataframe.index,
            y=dataframe.n_very_bearish,
            offsetgroup=0,
            marker_color='red',
        ),
        row=2,
        col=1,
    )

    fig.update_layout(hovermode='x unified')
    print('Plotting results...')
    fig.show()
