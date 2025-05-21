"""
Скачиваем историю BTC-USDT с OKX на любой глубине.
pip install pandas openpyxl requests
"""
import requests, pandas as pd, time

BASE   = "https://www.okx.com/api/v5/market"
EP     = "candles"            # можно 'history-candles' для очень старых данных
INST   = "BTC-USDT"
BAR    = "2H"                 # таймфрейм
PER_REQ= 300                  # лимит энд-пойнта ('candles' = 300, 'history-candles' = 100)
MAX    = 1000                 # сколько строк нужно в итоге
TZ     = "Asia/Tokyo"         # ваш часовой пояс

def fetch_okx_klines(max_rows: int = MAX):
    after = None              # «якорь» для пагинации
    out   = []

    while len(out) < max_rows:
        params = dict(instId=INST, bar=BAR, limit=PER_REQ)
        if after:
            params["after"] = after        # вернёт свечи старше этого ts

        r = requests.get(f"{BASE}/{EP}", params=params, timeout=10)
        r.raise_for_status()
        j = r.json()
        if j["code"] != "0":
            raise RuntimeError(j["msg"])

        batch = j["data"]
        if not batch:
            break                          # дошли до края истории

        out.extend(batch)
        after = batch[-1][0]               # самый старый ts в пакете
        time.sleep(0.12)                   # 8-9 req/сек — безопасно (<20/2 c)

        if len(batch) < PER_REQ:           # биржа отдала меньше, чем могла
            break

    return out[:max_rows]                  # на случай, если берем «с запасом»

rows = fetch_okx_klines()

# ---- в DataFrame ------------------------------------------------------------
cols = ["ts","open","high","low","close","volume"]
df = pd.DataFrame([[r[i] for i in range(6)] for r in rows], columns=cols)

df["ts"] = (
    pd.to_datetime(df["ts"], unit="ms", utc=True)
      .dt.tz_convert(TZ)
      .dt.tz_localize(None)                # Excel не понимает tz-aware
)
numcols = ["open","high","low","close","volume"]
df[numcols] = df[numcols].astype(float)
df["avg_price"] = df[["high","low"]].mean(axis=1)

df.sort_values("ts", inplace=True, ignore_index=True)
df.to_excel("BTCUSDT_okx_full.xlsx", index=False)
print(f"✅ Готово! Сохранено {len(df)} строк.")
