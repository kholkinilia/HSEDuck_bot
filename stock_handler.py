import requests
import json

base_urls = ["https://cloud.iexapis.com", "https://sandbox.iexapis.com"]
tokens = []
f = open("config.txt", "r")
for i in range(3):
    cur_token = f.readline()
    tokens.append(cur_token[:len(cur_token) - 1:])

cur_type = 1
base_url = base_urls[cur_type]
version = "stable"
token = tokens[cur_type]
base_params = {
    "token": token
}


def get_best_matches(s):
    url = "https://www.alphavantage.co/query"
    querystring = {"keywords": s, "function": "SYMBOL_SEARCH", "datatype": "json", "apikey": token[2]}
    response = requests.get(url, params=querystring)
    # print("RESPONSE: ", response.text)
    try:
        return response.json()
    except ValueError:
        return {"message": "failed"}


def get_type():
    global cur_type
    return cur_type


def switch_type():
    global cur_type, token, tokens, base_urls, base_url
    cur_type = 1 - cur_type
    base_url = base_urls[cur_type]
    token = tokens[cur_type]
    base_params["token"] = token
    print("TYPE SWITCHED TO: ", cur_type)


def get_multiple_quote(symbols):
    params = base_params
    params["types"] = "quote"
    symbols_param = ','.join(symbols)
    url = f"{base_url}/{version}/stock/market/batch?types=quote&token={token}&symbols={symbols_param}"
    result = requests.get(url)
    # print("RESP: ", result.text)
    try:
        return result.json()
    except ValueError:
        return {}


def get_price(symbol):
    params = base_params
    params["chartIEXOnly"] = "True"
    result = requests.get(f"{base_url}/{version}/stock/{symbol}/quote/latestPrice", params=params)
    # print("RESP: ", result.text)
    try:
        return float(result.text)
    except ValueError:
        return -1


def get_quote(symbol):
    params = base_params
    params["chartIEXOnly"] = "True"
    result = requests.get(f"{base_url}/{version}/stock/{symbol}/quote", params=params)
    # print("RESP: ", result.text)
    try:
        return result.json()
    except ValueError:
        return {}


if __name__ == "__main__":
    # data = get_multiple_quote(["Intl", "aapl", "twtr", "FB"])
    # print(data)
    # switch_type()
    # sp = get_quote("SPCE")
    # print(sp)
    # for key in data:
    #     print(f"========== {key} ==========")
    #     for value in data[key]:
    #         print(f"{value}: {data[key]}")
    json = get_best_matches("Microsoft")
