import yfinance as yf
import re

default_p_value = 0
default_d_value = 0
default_q_value = 0

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


if __name__ == "__main__":
    print(check_horizon('15'))
    print(parse_params_sarimax("r=1 q=2 d=3 p=1"))



















