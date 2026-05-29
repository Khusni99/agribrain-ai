Write-Host "Seeding AgriBrain Database..." -ForegroundColor Green
Set-Location -LiteralPath "..\backend"
python -c "
import asyncio
from app.db.seed import seed_database
asyncio.run(seed_database())
"
Write-Host "Database seeded successfully!" -ForegroundColor Green
