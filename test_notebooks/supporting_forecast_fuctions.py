import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import yfinance as yf

from statsmodels.tsa.api import VAR

def get_yfin_data(ticker, start_date = None, end_date = None):
    resultData = yf.download(ticker, start_date, end_date)

    resultData = resultData[["Open", "High","Low", "Close", "Adj Close", "Volume"]]
    return resultData


def plot_prediction(train_main_series, forecast_series, show_last_n =60 ):
    
    fig = go.Figure()


    fig.add_trace(go.Scatter(x=train_main_series.index[-show_last_n:], y=train_main_series.iloc[-show_last_n:],
                        mode='lines',
                        name='History'))
        
    fig.add_trace(go.Scatter(x = forecast_series.index, y = forecast_series.values,
                        mode='lines',
                        name='Predict'))
    
    fig.update_layout(
        autosize=False,
        width=500,
        height=500,
    )
    return fig

from sklearn.metrics import mean_absolute_percentage_error  as mape
from sklearn.metrics import mean_absolute_error  as mae
from sklearn.metrics import mean_squared_error  as mse


def get_metrics(y_true, y_pred):
    y_pred = np.array(y_pred)
    y_true = np.array(y_true)
    res = {}
    res['MAE'] = mae(y_true, y_pred)
    res['MAPE'] = mape(y_true, y_pred)
    res['RMSE'] = mse(y_true, y_pred)**(1/2)
    return res

#####EXP_SM

from statsmodels.tsa.api import ExponentialSmoothing

def evaluate_exp_sm(train_main_series, kwargs_model, steps = [60, 30, 14, 7]):
    metrics_df = pd.DataFrame(index = ['MAE', 'MAPE', 'RMSE'])

    for step in steps:
        fitted_model = ExponentialSmoothing(train_main_series[:-step], **kwargs_model).fit()
        forecast = fitted_model.forecast(step)
        metrics_df[step] = get_metrics(train_main_series[-step:], forecast).values()
    return metrics_df


#####SARIMA

from statsmodels.tsa.statespace.sarimax import SARIMAX

def evaluate_sarima(data, kwargs_model, steps = [60, 30, 14, 7]):
        metrics_df = pd.DataFrame(index = ['MAE', 'MAPE', 'RMSE'])
        for step in steps:
            fitted_model = SARIMAX(data[:-step]['Close'], **kwargs_model).fit()
            forecast = fitted_model.forecast(step)
            metrics_df[step] = get_metrics(data[-step:]['Close'], forecast).values()
        return metrics_df

#####VAR

def evaluate_VAR(data, kwargs_model, steps = [60, 30, 14, 7]):
        metrics_df = pd.DataFrame(index = ['MAE', 'MAPE', 'RMSE'])
        for step in steps:
            VAR_model = VAR(data)
            VAR_model_res = VAR_model.fit(**kwargs_model)       
            forecast = VAR_model_res.forecast(data.values, step)
            metrics_df[step] = get_metrics(data[-step:]['Close'], forecast[:, 3]).values()
        return metrics_df


####CatBoost

from catboost import CatBoostRegressor

def evaluate_catboost(data, steps = [60, 30, 14, 7]):
    metrics_df = pd.DataFrame(index = ['MAE', 'MAPE', 'RMSE'])
    for step in steps:

        x_train = data.iloc[:-step,-51:-3]
        y_train = data[:-step]['Close']

        model = CatBoostRegressor(iterations= 500, loss_function= 'MAE')
        model.fit(x_train, y_train)

        x_pred = data.iloc[-step:,:48]
        x_pred.columns = data.iloc[-step:,-51:-3].columns

        y_pred = model.predict(x_pred)
        diff = y_pred[0] - y_train[-1]
        forecast = y_pred-diff

        metrics_df[step] = get_metrics(data[-step:]['Close'], forecast).values()
    return metrics_df

def add_lags(x_df: pd.DataFrame, nlags, dropna: bool = True, cols=None) -> pd.DataFrame:
    ans_df = x_df.copy()
    if cols is None:
        cols = ans_df.columns
    for i in range(1, nlags + 1):
        ans_df = ans_df.join(x_df[cols].shift(i), rsuffix=f'_lag{i}')

    if dropna:
        ans_df = ans_df.dropna()
    return ans_df

def encode_time(datatime_index, label=None):
    res = pd.DataFrame(index  = datatime_index)
    res['quarter'] = res.index.quarter
    res['month'] = res.index.month
    res['year'] = res.index.year
    return res

def add_MA(x_df: pd.DataFrame, windows = [3, 6, 9], dropna: bool = True, cols=None) -> pd.DataFrame:
    ans_df = x_df.copy()
    if cols is None:
        cols = ans_df.columns
    for i in windows:
        ans_df = ans_df.join(x_df[cols].rolling(window=i).mean(),  rsuffix=f'MA{i}')

    if dropna:
        ans_df = ans_df.dropna()
    return ans_df

