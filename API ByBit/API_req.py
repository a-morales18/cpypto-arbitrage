import requests

url = "https://api.bybit.com/v5/market/tickers?category=spot&symbol=BTCUSDT"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
