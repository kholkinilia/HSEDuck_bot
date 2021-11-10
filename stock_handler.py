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


def get_quote_info(symbol):
    params = base_params
    params["chartIEXOnly"] = "True"
    result = requests.get(f"{base_url}/{version}/stock/{symbol}/quote/", params=params)
    try:
        return result.json()
    except json.decoder.JSONDecodeError:
        return {}


if __name__ == "__main__":
    data = get_quote_info("Intl")
    print(data)
    for key in data:
        print(key, ": '", data[key], "'", sep="")
