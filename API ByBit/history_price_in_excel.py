"""
Сохраняем историю цен BTC-USDT (Bybit) в Excel-таблицу.
pip install pandas openpyxl requests
"""
import requests
import pandas as pd
from datetime import datetime, timezone

# --- 1. параметры запроса ----------------------------------------------------
BASE_URL = "https://api.bybit.com"
ENDPOINT = "/v5/market/kline"
PARAMS = {
    "category": "linear",     # фьючерсы USDT-m
    "symbol":   "BTCUSDT",
    "interval": "120",         # дневная свеча; можно 1,3,5,15,30,60…
    "limit":    1000        # сколько баров вернуть (≤ 1000)
}

# --- 2. запрос и первичная проверка ------------------------------------------
resp = requests.get(BASE_URL + ENDPOINT, params=PARAMS, timeout=10)
resp.raise_for_status()                        # HTTP-ошибки → исключение
data = resp.json()

print (f"Получено {len(data['result']['list'])} свечей")

if data.get("retCode") != 0:
    raise RuntimeError(f'API error: {data.get("retMsg")}')

klines = data["result"]["list"]                # список свечей (последняя — 0-й элемент)

# --- 3. превращаем в DataFrame ----------------------------------------------
cols = [
    "start_time", "open", "high", "low", "close",
    "volume", "turnover"      # turnover = объём в quote-валюте
]
df = pd.DataFrame(klines, columns=cols)

# Timestamp приходит миллисекундами → datetime (UTC)
# 4-а. преобразуем start_time в datetime и убираем информацию о часовом поясе (Excel не поддерживает tz-aware)
df["start_time"] = pd.to_datetime(df["start_time"], unit="ms", utc=True).dt.tz_localize(None)

# Числовые столбцы к float/int
num_cols = ["open", "high", "low", "close", "volume", "turnover"]
df[num_cols] = df[num_cols].astype(float)

df["avg_price"] = df[["high", "low"]].mean(axis=1)

# --- 4. сортировка от старого к новому ---------------------------------------
df.sort_values("start_time", inplace=True, ignore_index=True)

# --- 5. экспорт в Excel ------------------------------------------------------
out_file = "BTCUSDT_90d_bybit.xlsx"
df.to_excel(out_file, index=False)             # openpyxl создаст файл

print(f"✅ Готово! Сохранено {len(df)} строк в «{out_file}»")
