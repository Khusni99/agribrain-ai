Write-Host "Starting AgriBrain AI Development Server..." -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path "..\backend\.env")) {
    Copy-Item "..\backend\.env.example" "..\backend\.env"
    Write-Host "Created .env from .env.example - please update with your settings" -ForegroundColor Yellow
}

# Start API server
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Cyan
Set-Location -LiteralPath "..\backend"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
