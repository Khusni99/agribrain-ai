# AgriBrain AI API Documentation

## Base URL
`http://localhost:8000/api/v1`

## Authentication

### Register
`POST /auth/register`

```json
{
  "email": "farmer@example.com",
  "username": "farmer1",
  "password": "securepassword",
  "full_name": "Pak Tani",
  "phone": "08123456789"
}
```

### Login
`POST /auth/login`

```json
{
  "username": "farmer1",
  "password": "securepassword"
}
```

Response:
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": { ... }
}
```

## Diagnosis

### AI Agronomist
`POST /diagnosis/ask`
Authorization: Bearer token

```json
{
  "query": "Tanaman cabai 45 HST, daun atas kecil, daun bawah hijau tua, curah hujan tinggi",
  "crop_type": "chili",
  "language": "id"
}
```

### Disease Detection
`POST /diagnosis/detect-disease`
Multipart form with image file

### Fertilizer Recommendation
`POST /diagnosis/fertilizer-recommend`

## Farms

### List Farms
`GET /farms`

### Create Farm
`POST /farms`

### Create Field
`POST /farms/{farm_id}/fields`

## Weather

### Current Weather
`GET /weather/current?lat=-6.2&lon=106.8`

### Forecast
`GET /weather/forecast?lat=-6.2&lon=106.8&days=7`

### Alerts
`GET /weather/alerts?lat=-6.2&lon=106.8&crop_type=chili`

## Cost Calculator

### Calculate
`POST /cost/calculate`

## Marketplace

### Products
`GET /marketplace/products`

### Market Prices
`GET /marketplace/prices`
