# AgriBrain AI - Testing Guide

## Prerequisites

- Python 3.12+
- pip

## Setup

```powershell
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Seed database
python -m app.db.seed
```

## Running Tests

```powershell
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_health.py -v
pytest tests/test_diagnosis.py -v
pytest tests/test_weather.py -v
```

## Running the Server

```powershell
# Start development server
uvicorn app.main:app --reload

# Server runs at: http://localhost:8000
# API docs at: http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

## API Endpoint Testing

### 1. Register User
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/register" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"farmer@farm.com","username":"farmer1","password":"secret123","full_name":"Pak Tani"}'
```

### 2. Login
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"farmer1","password":"secret123"}'
```

### 3. AI Diagnosis
```powershell
$token = "YOUR_TOKEN_HERE"
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/diagnosis/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Headers @{Authorization = "Bearer $token"} `
  -Body '{"query":"Daun cabai menguning bagian bawah","crop_type":"chili","language":"id"}'
```

### 4. Cost Calculator
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/cost/calculate" `
  -Method POST `
  -ContentType "application/json" `
  -Headers @{Authorization = "Bearer $token"} `
  -Body '{"field_id":1,"crop_type":"chili","area_hectare":1.0,"items":[{"name":"Benih","quantity":1,"unit":"kg","unit_price":500000,"total_cost":500000},{"name":"Pupuk NPK","quantity":400,"unit":"kg","unit_price":4000,"total_cost":1600000}]}'
```

### 5. Marketplace Products
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/marketplace/products"
```

### 6. Market Prices
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/marketplace/prices"
```

### 7. Current Weather
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/weather/current?lat=-6.2&lon=106.8"
```

### 8. Disease Detection (Upload Image)
```powershell
# Requires Postman or similar tool for multipart upload
# POST http://localhost:8000/api/v1/diagnosis/detect-disease
# Form-data: file=@photo.jpg
```

## Expected Results

| Endpoint | Status | Description |
|---|---|---|
| `POST /auth/register` | 201 | Returns access_token + user data |
| `POST /auth/login` | 200 | Returns access_token |
| `POST /diagnosis/ask` | 200 | Returns diagnosis with confidence score |
| `POST /cost/calculate` | 200 | Returns cost breakdown + ROI |
| `GET /marketplace/products` | 200 | Returns product list |
| `GET /marketplace/prices` | 200 | Returns market prices |
| `GET /weather/current` | 200 | Returns weather + disease risk |
| `GET /health` | 200 | `{"status": "healthy"}` |
| `GET /docs` | 200 | Swagger UI loads |

## Database

The app uses **SQLite** by default (`agribrain_dev.db` in the backend directory).

For PostgreSQL, set environment variable `USE_POSTGRES=1` and configure `POSTGRES_*` settings.

### Reset Database
```powershell
Remove-Item -LiteralPath "backend/agribrain_dev.db"
python -m app.db.seed
```

## Test Credentials (after seed)

- **Username:** `demo`
- **Password:** `demo123`
