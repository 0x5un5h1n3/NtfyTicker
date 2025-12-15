# NtfyTicker

Asset price monitoring with ntfy push notifications. FastAPI + SQLite + configurable price feeds.

## 🚀 Quick Start

1. Clone & install
```sh
git clone https://github.com/0x5un5h1n3/NtfyTicker.git
```
```sh
cd NtfyTicker
```
```py
pip install -r requirements.txt
```
2. Copy config
```sh
cp .env.example .env
```
3. Run
```py
uvicorn src.main:app --reload
```

**API docs:** http://localhost:8000/docs

## 📱 Test with ntfy app

1. Open ntfy app (iOS/Android/web)
2. Subscribe to topic: `test-topic`

3. Create alert:

```sh
curl -X POST "http://localhost:8000/asset-alerts"
-H "Content-Type: application/json"
-d '{
"symbol": "ASSET1",
"asset_type": "asset1",
"direction": "above",
"target_price": 20000,
"ntfy_topic": "test-topic"
}'
```

✅ Get notified when price hits threshold!

## 🔧 Configuration (.env)

```
NTFY_BASE_URL=https://ntfy.sh
ASSET_PRICE_URL=https://api.stonks.com/api/v3/simple/price
CHECK_INTERVAL_SECONDS=30
DATABASE_URL=sqlite:///alerts.db
LOG_LEVEL=INFO
```

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service status |
| `GET` | `/asset-alerts` | List active alerts |
| `POST` | `/asset-alerts` | Create alert |
| `DELETE` | `/asset-alerts/{id}` | Delete alert |

## 🛠 Tech Stack

- **FastAPI** - API framework
- **SQLAlchemy** - SQLite ORM
- **APScheduler** - Background jobs
- **httpx** - HTTP client
- **Pydantic** - Config + models
- **ntfy.sh** - Push notifications

## 📦 Deploy

```sh
Docker (add Dockerfile)
docker build -t ntfyticker .
docker run -p 8000:8000 ntfyticker
```

## Supported Assets


Edit `src/price_providers.py` mapping:
```py
mapping = {
"ASSET1": "asset1",
"ASSET2": "asset2",
# Add your assets here
}
```
