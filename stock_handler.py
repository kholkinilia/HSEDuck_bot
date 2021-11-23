import requests
import json

base_urls = ["https://cloud.iexapis.com", "https://sandbox.iexapis.com"]
tokens = ["pk_ca70a8bf897d4585b98de97b68a74aec", "Tpk_cac5fe3098e3408386a98adf88931ba9"]

cur_type = 1
base_url = base_urls[cur_type]
version = "stable"
token = tokens[cur_type]
base_params = {
    "token": token
}


def get_best_matches(s):
    print(s)
    url = "https://alpha-vantage.p.rapidapi.com/query"
    querystring = {"keywords": s, "function": "SYMBOL_SEARCH", "datatype": "json"}
    headers = {
        'x-rapidapi-host': "alpha-vantage.p.rapidapi.com",
        'x-rapidapi-key': "e06451b9b4msh6de7f3ea5338f35p158178jsn47f40be3ab7f"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.text)
    try:
        return response.json()
    except json.decoder.JSONDecodeError:
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
    try:
        return result.json()
    except json.decoder.JSONDecodeError:
        return {}


def get_price(symbol):
    params = base_params
    params["chartIEXOnly"] = "True"
    result = requests.get(f"{base_url}/{version}/stock/{symbol}/quote/latestPrice", params=params)
    print(result.text)
    try:
        return float(result.text)
    except ValueError:
        # TODO: check if it actually is a ValueError
        return -1


def get_quote(symbol):
    params = base_params
    params["chartIEXOnly"] = "True"
    result = requests.get(f"{base_url}/{version}/stock/{symbol}/quote/", params=params)
    print(result.text)
    try:
        return result.json()
    except json.decoder.JSONDecodeError:
        return {}


if __name__ == "__main__":
    data = get_multiple_quote(["Intl", "aapl", "twtr", "FB"])
    print(data)
    switch_type()
    sp = get_quote("SPCE")
    print(sp)
    for key in data:
        print(f"========== {key} ==========")
        for value in data[key]:
            print(f"{value}: {data[key]}")
