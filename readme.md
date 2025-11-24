# 🌦️ Weather Station Data API

This project ingests weather data from S3, stores it in PostgreSQL, computes annual statistics, and serves it via a RESTful FastAPI.

---

## 📦 Project Structure

├── app/
│ ├── db/
│ ├── routers/
│ ├── ingest.py
│ ├── analysis.py
│ └── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── start_worker.sh
├── .env.example
├── tests/
└── README.md

---

## How to Run Locally

### 1. Clone the Repo

```bash
git clone https://github.com/meghanaavadhanam/WeatherAPI.git
cd src
```

### 2. Set Up Environment Variables and change them as required (You will need AWS creds and DB URL)

```bash
cp .env.example .env
```

### 3. Start Postgres (via Docker)

```bash
docker compose up -d postgres
```

### 4. Run the App

```bash
docker compose up --build
```

### The API will be live with weather data and analysis data at:

`http://localhost:8000/docs#`


### Running Tests (Optional)


