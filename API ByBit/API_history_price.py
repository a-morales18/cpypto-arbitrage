import requests

url = "https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval=d&limit=90"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
