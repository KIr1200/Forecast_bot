import yfinance as yf
import re
import telebot
from telebot import types
import os
import time

default_p_value = 1
default_d_value = 1
default_q_value = 1

#TODO
def check_ticker(ticker):
    startDate = '2015-03-01'
    endDate = '2017-03-07'
    resultData = yf.download(ticker, startDate, endDate)
    print(resultData)
    if(resultData.empty):
        return "Wrong ticker"
    else:
        return "good"


def check_horizon(horizon):
    if re.match("^-?\d+?$",horizon) is None:
        return -3
    if(int(horizon) <= 0):
        return -1
    if(int(horizon) > 120):
        return -2
    return int(horizon)


def parse_params_sarimax(params):
    p = default_p_value
    d = default_d_value
    q = default_q_value

    if not (re.search(r"p ?= ?-?\d+", params) is None):
        result = int(re.search(r"p ?= ?-?\d+", params).group().replace('p','').replace('=',''))
        if (result >=0):
            p = result

    if not (re.search(r"d ?= ?-?\d+", params) is None):
        result = int(re.search(r"d ?= ?-?\d+", params).group().replace('d','').replace('=',''))
        if (result >=0):
            d = result

    if not (re.search(r"q ?= ?-?\d+", params) is None):
        result = int(re.search(r"q ?= ?-?\d+", params).group().replace('q','').replace('=',''))
        if (result >=0):
            q = result

    return {'order' : (p, d, q)}


def print_png_and_data(user_id, bot):
    count = 0
    while(not (os.path.exists(f"{user_id}_forecast.png") and os.path.exists(f"{user_id}_metrics_table.txt") 
               and os.path.exists(f"{user_id}_metrics_table.png") and os.path.exists(f"{user_id}_predict.csv")) and count <=5):
        count += 1
        time.sleep(1)
    if (count > 5):
        bot.send_message(user_id, 'Произошла ошибка, попробуйте снова')
    else:
        with open (f"{user_id}_forecast.png", 'rb') as png:
            bot.send_message(user_id, "График предсказания")
            bot.send_photo(user_id, png)
        os.remove(f"{user_id}_forecast.png")
        with open (f"{user_id}_metrics_table.png", 'rb') as png:
            bot.send_message(user_id, "Метрики за последние 60, 30, 14, 7 дней")
            bot.send_photo(user_id, png)
        os.remove(f"{user_id}_metrics_table.png")
        with open (f"{user_id}_predict.csv", 'rb') as csv:
            bot.send_message(user_id, "Прогноз на указанный горизонт")
            bot.send_document(user_id, csv)
        os.remove(f"{user_id}_predict.csv")
        
        '''with open (f"{user_id}_metrics_table.txt", 'rb') as file:
            data = file.read()
            bot.send_message(user_id, data)'''

    '''while(not os.path.exists(f"{user_id}_metrics_table.png") and count <=5):
        count += 1
        time.sleep(1)
    if (count > 5):
        bot.send_message(user_id, 'Произошла ошибка, попробуйте снова')
    else:
        with open (f"{user_id}_metrics_table.png", 'rb') as png:
            bot.send_photo(user_id, png)
        os.remove(f"{user_id}_metrics_table.png")

    while(not os.path.exists(f"{user_id}_metrics_table.txt") and count <=5):
        count += 1
        time.sleep(1)
    if (count > 5):
        bot.send_message(user_id, 'Произошла ошибка, попробуйте снова')
    else:
        with open (f"{user_id}_metrics_table.txt", 'rb') as png:
            bot.send_document(user_id, png)
        os.remove(f"{user_id}_metrics_table.txt")'''



if __name__ == "__main__":
    print(check_horizon('15'))
    print(parse_params_sarimax("r=1 q=2 d=3 p=1"))



















