"""
TODO: General
1. Obtener correlacion entre precio de cierre y score positivo, negativo, neutral 
"""
import warnings

warnings.filterwarnings('ignore')
import os
from pathlib import Path
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
import pandas_datareader as pdr
from tqdm import tqdm 
from textblob import TextBlob

# Visualization
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


############################################################################
# Settings
############################################################################

WRITE_CSV = False
PLOT_RESULTS = True
TICKER = 'BTC-USD'


data_path = Path('data')
if not data_path.exists():
    data_path.mkdir(parents=True)

############################################################################
# Funciones Dataframes (armar, agrupar, etc...)
############################################################################

def estimate_polarity(text: str):
  # A partir de un string calcula su polaridad
  return TextBlob(text).sentiment.polarity

def load_and_estimate(file_name: str):
  # Cargamos las noticias en csv
  # Ordenamos por fecha (vienen desordenados desde la extraccion)
  # Aplicamos TextBlob para obtener polaridad
  test =  pd.read_csv(os.path.join(data_path, file_name), 
    sep='|', 
    parse_dates=['date'],
    date_parser=lambda col: pd.to_datetime(col, utc=True),
    infer_datetime_format=True
    )
  test = test.sort_values(by='date')
  test.set_index('date')
  test['polarity'] = test.text.apply(estimate_polarity)
  return test


def group_news(test: DataFrame):
  print('Agrupando positivos, negativos y neutrales...')
  temp = dict()
  for row in tqdm(test.values):
    row_date = row[1].date().strftime('%Y-%m-%d')
    if row_date not in temp:
      # en orden 0: positives, 1: neutral-postive, 2: neutral, 3: neutral-negative, 4: negatives,
      temp[row_date] = [0,0,0,0,0] 
    polarity = row[2]
    if polarity == 0.0: # neutral
      temp[row_date][2] += 1
    if polarity > 0.0 and polarity < 0.4: # neutral-positive
      temp[row_date][1] += 1
    if polarity > 0.0 and polarity > 0.5: # postive
      temp[row_date][0] += 1 
    if polarity < 0.0 and polarity > -0.5: # neutral-negative
      temp[row_date][3] += 1
    if polarity < 0.0 and polarity < -0.5: # negative
      temp[row_date][4] += 1
  return temp

def get_historical_price_with_polarity(test: DataFrame, ticker: str):
  # Procedemos a obtener data historica del BTC segun lo extraido
  start_date = test.iloc[0].date
  end_date = test.iloc[-1].date
  print(f'Fecha inicial: {start_date} \nFecha final: {end_date}')
  btc = pdr.DataReader(ticker,'yahoo',start_date,end_date)

  results = group_news(test)
  print(f'Generando dataframe ticker: {ticker}')
  
  # Aplicamos columnas a sus filas respecitvas a partir de la fecha
  btc['positives'] = btc.apply(lambda x: results[x.name.date().strftime('%Y-%m-%d')][0] if x.name.date().strftime('%Y-%m-%d') in results.keys() else 0 , axis=1)
  btc['negatives'] = btc.apply(lambda x: results[x.name.date().strftime('%Y-%m-%d')][4] if x.name.date().strftime('%Y-%m-%d') in results.keys() else 0, axis=1)
  btc['neutral_positives'] = btc.apply(lambda x: results[x.name.date().strftime('%Y-%m-%d')][1] if x.name.date().strftime('%Y-%m-%d') in results.keys() else 0 , axis=1)
  btc['neutral_negatives'] = btc.apply(lambda x: results[x.name.date().strftime('%Y-%m-%d')][3] if x.name.date().strftime('%Y-%m-%d') in results.keys() else 0, axis=1)
  btc['neutral'] = btc.apply(lambda x: results[x.name.date().strftime('%Y-%m-%d')][2] if x.name.date().strftime('%Y-%m-%d') in results.keys() else 0, axis=1)
  btc['change_24hrs'] = btc.apply(lambda x: (x['Close']*100.0 / x['Open'] - 100.0), axis=1)
  
  all_time_high = btc['High'].max()
  print(f'Máximo alcanzado: $ {all_time_high:3.2f} [USD]')
  
  btc['High'] = btc['High'] / all_time_high
  btc['Low'] = btc['Low'] / all_time_high
  btc['Open'] = btc['Open'] / all_time_high
  btc['Close'] = btc['Close'] / all_time_high
  corr_matrix = btc.corr(method='pearson')

  # Recortamos el dataframe para solo obtener datoas de este año (2021)
  return_start_date = "2020-12-31"
  after_start_date = btc.index >= return_start_date
  filtered_dates = btc.loc[after_start_date]

  print('Dataframe generado!')
  return filtered_dates, corr_matrix

############################################################################
# Funciones Miscelaneas (exports, plots, etc...)
############################################################################

def export_csv(file_name: str, dataframe: DataFrame):
  # Escribe el dataframe en un archivo csv
  print(f'Exportando resultados en: {file_name}')
  output_file = open(file_name, 'w')
  btc.to_csv(path_or_buf=output_file,index=True, sep='|')
  output_file.close()
  print('Exportado exitoso!')

def plot_results(dataframe: DataFrame, corr_matrix, ticker: str):
  # Subplot con plotly
  # Grafico de velas con barras apiladas
  fig = make_subplots(rows=2, cols=1, shared_xaxes=True,  vertical_spacing=0.05)
  # fig.add_trace(go.Candlestick(x=dataframe.index,
  #                 open=dataframe['Open'],
  #                 high=dataframe['High'],
  #                 low=dataframe['Low'],
  #                 close=dataframe['Close'],
  #                 name=f'Price {ticker}'), row=1, col=1)
  fig.add_trace(go.Bar(name='24h Variation', x=dataframe.index, y=dataframe.change_24hrs, offsetgroup=0), row=1, col=1)
  
  # fig.add_trace(go.Heatmap(
  #        z=corr_matrix.values,
  #        x=['High', 'Low', 'Open', 'Close', 'Volume', 'Adj Close', 'positives', 'negatives', 'neutral', 'change_24hrs'],
  #        y=['High', 'Low', 'Open', 'Close', 'Volume', 'Adj Close', 'positives', 'negatives', 'neutral', 'change_24hrs'],
  #        type='heatmap',
  #        colorscale='Viridis'), row=3, col=1)
  
  # Barras apiladas para ver graficamente
  # ratio positvo/negativo del dia
  fig.add_trace(go.Bar(
      name="Positives",
      x = dataframe.index,
      y = dataframe.positives,
      offsetgroup=0,
      marker_color='green'
  ), row=2, col=1)

  fig.add_trace(go.Bar(
      name="Neutral-Positives",
      x = dataframe.index,
      y = dataframe.neutral_positives,
      offsetgroup=0,
      marker_color='lightgreen'
  ), row=2, col=1)

  fig.add_trace(go.Bar(
      name="Neutral-Negatives",
      x = dataframe.index,
      y = dataframe.neutral_negatives,
      offsetgroup=0,
      marker_color='orange'
  ), row=2, col=1)

  fig.add_trace(go.Bar(
      name="Negatives",
      x = dataframe.index,
      y = dataframe.negatives,
      offsetgroup=0,
      marker_color='red'
  ), row=2, col=1)

  fig.update_layout(hovermode="x unified")
  print('Mostrando grafico...')
  fig2 = go.Figure(data=go.Heatmap(
                    z=corr_matrix,
                    x=['High', 'Low', 'Open', 'Close', 'Volume', 'Adj Close', 'positives', 'negatives', 'neutral_positives', 'neutral_negatives', 'neutral', 'change_24hrs'],
                    y=['High', 'Low', 'Open', 'Close', 'Volume', 'Adj Close', 'positives', 'negatives', 'neutral_positives', 'neutral_negatives', 'neutral', 'change_24hrs'],))
  fig.show()
  fig2.show()



if __name__ == "__main__":
  test = load_and_estimate('test.csv')
  btc, corr_matrix = get_historical_price_with_polarity(test, TICKER)

  # Export a csv de los resultados
  if WRITE_CSV:
    export_csv('BTC-USD-polarity.csv', btc)
    
  if PLOT_RESULTS:
    plot_results(btc, corr_matrix, TICKER)