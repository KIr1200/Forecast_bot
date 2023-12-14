import json
import numpy as np
import pandas as pd

from statsmodels.tsa.api import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from catboost import CatBoostRegressor

from supporting_forecast_fuctions import *





def run_forecast(argv):
    print(argv)
    user_id = argv[0]
    ticker = argv[1]
    horizon  = argv[2]
    name_model  = argv[3]

    #with open(str(user_id) + '_add_params.json') as json_file:
    #    add_params = json.load(json_file)

    with open(str(user_id) + '_kwargs_model.json') as json_file:
        kwargs_model  = json.load(json_file)

    #with open(str(user_id) + '_add_data.json') as json_file:
    #    add_data = pd.read_csv(json_file)

    yf_data = get_yfin_data(ticker)




    if name_model == 'EXPONENTIAL_SMOOTHING':
        print(123)

        train_main_series = yf_data['Close']

        exp_sm = ExponentialSmoothing(
            train_main_series,
            **kwargs_model
        ).fit()

        forecast_numpy = exp_sm.forecast(horizon).values
        forecast_series = pd.Series(data = forecast_numpy, index=pd.date_range(train_main_series.index[-1], periods=horizon))
        metrics_df = evaluate_exp_sm(train_main_series, kwargs_model)
        fig_forecast  = plot_prediction(train_main_series,forecast_series)
        
    elif name_model == 'VAR':
        train_main_series  = yf_data['Close']

        VAR_model = VAR(yf_data)
        VAR_model_res = VAR_model.fit(**kwargs_model)
        forecast_numpy = VAR_model_res.forecast(yf_data.values, horizon)
        forecast_df = pd.DataFrame(data = forecast_numpy, index=pd.date_range(yf_data.index[-1], periods=horizon), columns = yf_data.columns)
        forecast_series = forecast_df['Close']
        metrics_df = evaluate_VAR(yf_data, kwargs_model=kwargs_model)
        fig_forecast = plot_prediction(train_main_series,forecast_series)
    elif name_model == 'SARIMA':

        train_main_series = yf_data

        model = SARIMAX(train_main_series['Close'], **kwargs_model).fit()
        predict_numpy = model.forecast(steps = horizon).values

        forecast_numpy = evaluate_sarima(train_main_series, kwargs_model)
        forecast_series = pd.Series(data = forecast_numpy, index=pd.date_range(train_main_series.index[-1], periods=horizon))
        fig_forecast = plot_prediction(train_main_series['Close'],forecast_series)
        #fig.write_image("fig1.png")


    elif name_model == 'CATBOOST':
        train_main_series  = yf_data
        train_main_series = add_MA(train_main_series)
        train_main_series = add_lags(train_main_series, horizon+1)
        train_main_series = pd.concat([train_main_series, encode_time(train_main_series.index)], axis=1)
        x_train = train_main_series.iloc[:,-51:-3]
        y_train = train_main_series['Close']

        model = CatBoostRegressor(iterations= 500, loss_function= 'MAE')
        model.fit(x_train, y_train)
        
        x_pred = train_main_series.iloc[-horizon:,:48]
        x_pred.columns = train_main_series.iloc[-horizon:,-51:-3].columns

        y_pred = model.predict(x_pred)
        diff = y_pred[0] - y_train[-1]
        forecast_numpy = y_pred - diff
        forecast_series = pd.Series(data = y_pred, index=pd.date_range(train_main_series.index[-1], periods=horizon))
        fig_forecast = plot_prediction(train_main_series['Close'],forecast_series)
        metrics_df = evaluate_catboost(train_main_series)
    else:
        return 1

    fig_forecast.write_image(str(user_id) + '_forecast.png', engine="orca")
