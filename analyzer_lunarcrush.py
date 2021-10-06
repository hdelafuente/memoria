import json
import requests
import pandas as pd
import datetime as dt
# Visualization
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots



ticker = 'BTC'
api_url = 'https://api.lunarcrush.com/v2?'
start = 1609415999 #'2020-12-31'
end = 1632571199 #'2021-09-25'
data_points = 760
print('Solicitando data...')
route = f'data=assets&key=05cvwkrenwftq8lhnyxgja&symbol={ticker}&interval=day&start={start}&end={end}&data_points={data_points}'
r = requests.get(api_url + route)
response = r.json()['data'][0]
extracted_days = len(response['timeSeries'])

print(f'Extraida información de {extracted_days} días')

data = {
  'time': [],
  'n_very_bearish': [],
  'n_bearish': [],
  'n_neutral': [],
  'n_bullish': [],
  'n_very_bullish': [],
  'galaxy_score': [],
  'change': [],
}
for i in response['timeSeries']:
  data['time'].append( i['time'])
  data['n_very_bearish'].append(i['tweet_sentiment1'])
  data['n_bearish'].append(i['tweet_sentiment2'])
  data['n_neutral'].append(i['tweet_sentiment3'])
  data['n_bullish'].append(i['tweet_sentiment4'])
  data['n_very_bullish'].append(i['tweet_sentiment5'])
  data['galaxy_score'].append(i['galaxy_score'])
  data['change'].append(i['close']*100.0 / i['open'] - 100.0)


fig = make_subplots(rows=2, cols=1, shared_xaxes=True,  vertical_spacing=0.05)
fig.add_trace(go.Bar(name='24h Variation', x=data['time'], y=data['change'], offsetgroup=0), row=1, col=1)
fig.add_trace(go.Bar(
      name="Positives",
      x = data['time'],
      y = data['n_very_bullish'],
      offsetgroup=0,
      marker_color='green'
  ), row=2, col=1)

fig.add_trace(go.Bar(
    name="Neutral-Positives",
    x = data['time'],
    y = data['n_bullish'],
    offsetgroup=0,
    marker_color='lightgreen'
), row=2, col=1)

fig.add_trace(go.Bar(
    name="Neutral-Negatives",
    x = data['time'],
    y = data['n_bearish'],
    offsetgroup=0,
    marker_color='orange'
), row=2, col=1)

fig.add_trace(go.Bar(
    name="Negatives",
    x = data['time'],
    y = data['n_very_bearish'],
    offsetgroup=0,
    marker_color='red'
), row=2, col=1)

fig.update_layout(hovermode="x unified")
fig.show()