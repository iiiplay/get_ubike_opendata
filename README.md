# get_ubike_opendata

定時抓取**台北市 YouBike 2.0 即時站點資料**，寫入 SQLite 資料庫累積成歷史紀錄。
由 GitHub Actions 每 10 分鐘自動執行一次，並把更新後的 `ubike.db` commit 回 repo。

## 資料來源

台北市政府開放資料 —— YouBike2.0 臺北市公共自行車即時資訊：

```
https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json
```

程式只保留 `act == 1`（營運中）的站點。

## 專案結構

| 檔案 | 用途 |
|---|---|
| `get_ubike_data.py` | 主程式：抓取 → 建表 → 寫入 SQLite，執行一次即結束 |
| `.github/workflows/ubike.yml` | GitHub Actions 排程（每 10 分鐘）＋ 自動 commit |
| `requirements.txt` | 相依套件（`pandas`） |
| `run.bat` | Windows 本機手動執行用 |
| `ubike.db` | 產生的 SQLite 資料庫（由 Actions 寫回 repo） |

## 資料表結構

資料庫 `ubike.db`，資料表 `taipei`：

| 欄位 | 型別 | 說明 |
|---|---|---|
| `mday` | text | 資料更新時間 |
| `sno` | int | 站點代號 |
| `sarea` | text | 行政區 |
| `sna` | text | 站點名稱 |
| `ar` | text | 地址 |
| `available_rent_bikes` | int | 可借車輛數 |
| `available_return_bikes` | int | 可還空位數 |
| `latitude` | float | 緯度 |
| `longitude` | float | 經度 |

主鍵為 `(sno, mday)`，寫入用 `insert or ignore`，因此同一站點同一時間戳只會存一筆，重複執行不會產生重複資料。

## 本機執行

```bash
pip install -r requirements.txt
python get_ubike_data.py
```

Windows 也可直接雙擊 `run.bat`。

執行後會在當前目錄產生（或更新）`ubike.db`，並印出本次寫入筆數：

```
-------------------------------------
2026-08-09 21:10:17.123456
共寫入 1234 筆資料
```

## 自動化排程

`.github/workflows/ubike.yml` 的行為：

- **觸發**：`cron: '*/10 * * * *'`（每 10 分鐘），另可在 GitHub 網頁用 `workflow_dispatch` 手動觸發。
- **時區**：`TZ: Asia/Taipei`，log 與 commit 訊息時間才正確。
- **併發控制**：`concurrency` 群組避免上一輪未結束就開下一輪造成 commit 衝突。
- **權限**：`contents: write`，才能把 `ubike.db` 推回 repo。
- **無新資料時**：`git diff --staged --quiet` 判斷無變更就略過 commit。

> GitHub 排程不保證準時，尖峰時段可能延遲數分鐘或偶爾跳過一次。若需要嚴格的固定頻率，得改用自架排程（例如本機工作排程器或雲端 VM 的 cron）。

## 查詢範例

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("ubike.db")

# 某站點的可借車輛數變化
df = pd.read_sql(
    "select mday, available_rent_bikes from taipei where sna like '%西門%' order by mday",
    conn,
)
print(df)

conn.close()
```

## 注意事項

- `ubike.db` 目前**不在 .gitignore 中**，且會由 Actions 持續 commit 回 repo，隨時間累積會讓 repo 體積不斷增長。長期運作建議定期清理歷史，或改存到外部資料庫／物件儲存。
- 資料來源為第三方服務，網址或欄位若變動，`get_ubike_data.py` 中的欄位清單需同步調整。
