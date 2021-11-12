import requests
import json

# base_url = "https://cloud.iexapis.com"
base_url = "https://sandbox.iexapis.com"
version = "stable"
# token = "pk_ca70a8bf897d4585b98de97b68a74aec"
token = "Tpk_cac5fe3098e3408386a98adf88931ba9"
base_params = {
    "token": token
}


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
    result = requests.get(f"{base_url}/{version}/stock/{symbol}/price/", params=params)
    try:
        return float(result.text)
    except ValueError:
        # TODO: check it actually is ValueError
        return -1


def get_quote(symbol):
    params = base_params
    params["chartIEXOnly"] = "True"
    result = requests.get(f"{base_url}/{version}/stock/{symbol}/quote/", params=params)
    try:
        return result.json()
    except json.decoder.JSONDecodeError:
        return {}


if __name__ == "__main__":
    data = get_multiple_quote(["Intl", "aapl", "twtr", "FB"])
    print(data)
    for key in data:
        print(f"========== {key} ==========")
        for value in data[key]:
            print(f"{value}: {data[key]}")
