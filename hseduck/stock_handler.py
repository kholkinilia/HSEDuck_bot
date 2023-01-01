import requests
import json
import os

base_urls = {
    "main": "https://cloud.iexapis.com",
    "sandbox": "https://sandbox.iexapis.com"
}
tokens = {
    "main": os.environ["HSEDUCK_BOT_IEXAPI_TOKEN_SECRET"],
    "sandbox": os.environ["HSEDUCK_BOT_IEXAPI_TOKEN_SANDBOX"]
}

valid_modes = {"main", "sandbox"}
mode = "sandbox"
base_url = base_urls[mode]
version = "stable"
token = tokens[mode]
base_params = {
    "token": token
}


def set_mode(new_mode):
    global mode, token, tokens, base_urls, base_url
    if new_mode not in valid_modes:
        return False
    mode = new_mode

    base_url = base_urls[mode]
    token = tokens[mode]
    base_params["token"] = token

    print("MODE SWITCHED TO: ", mode)
    return True


def switch_mode():
    global mode
    if mode == "main":
        set_mode("sandbox")
    else:
        set_mode("main")


def get_best_matches(s):
    url = "https://www.alphavantage.co/query"
    querystring = {"keywords": s, "function": "SYMBOL_SEARCH", "datatype": "json", "apikey": token[2]}
    response = requests.get(url, params=querystring)
    # print("RESPONSE: ", response.text)
    try:
        return response.json()
    except ValueError:
        return {"message": "failed"}


def get_mode():
    global mode
    return mode


def get_multiple_quote(symbols):
    params = base_params
    params["types"] = "quote"
    symbols_param = ','.join(symbols)
    url = f"{base_url}/{version}/stock/market/batch?types=quote&token={token}&symbols={symbols_param}"
    # print(url)
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
    # set_mode("main")
    response = get_multiple_quote(["INTL", "AAPL", "TWTR", "FB"])
    print(json.dumps(response, indent=2))
