# Deploy AgriBrain AI Backend to Render

## Prerequisites

- [Render](https://render.com) account
- [Neon](https://neon.tech) account with a PostgreSQL project
- Cloudinary account (for image upload)

---

## 1. Set Up Neon Database

1. Go to [console.neon.tech](https://console.neon.tech) and create a project.
2. Note the **connection string** — it looks like:
   ```
   postgresql://user:password@ep-xxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```
3. (Optional) Enable connection pooling by adding `-pooler` to the hostname:
   ```
   postgresql://user:password@ep-xxx-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```

> **Note:** The app automatically converts `sslmode=require` to `ssl=true` for SQLAlchemy/asyncpg compatibility.

---

## 2. Fork / Push Code to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git remote add origin https://github.com/<your-username>/agribrain-ai.git
git push -u origin main
```

---

## 3. Create Render Web Service

1. Go to [dashboard.render.com](https://dashboard.render.com) → **New +** → **Web Service**.
2. Connect your GitHub repository.
3. Fill in the form:

| Field | Value |
|---|---|
| **Name** | `agribrain-ai-api` |
| **Runtime** | `Python` |
| **Region** | `Singapore` (closest to Indonesia) |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

4. Add environment variables (see section below).
5. Click **Create Web Service**.

---

## 4. Environment Variables

Set these in **Render Dashboard → Environment**:

| Variable | Value |
|---|---|
| `DATABASE_URL` | `postgresql://user:password@ep-xxx-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require` |
| `SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `CLOUDINARY_CLOUD_NAME` | Your Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Your Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Your Cloudinary API secret |

Optional (add AI/weather features):

| Variable | Value |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4` (or your preferred model) |
| `WEATHER_API_KEY` | OpenWeatherMap API key |

> **Security:** `render.yaml` in the repo lists these with `sync: false` — values must be set manually in the Render dashboard. They are never committed.

---

## 5. Deployment Flow

Render will:

1. Pull code from GitHub
2. Install Python deps (`pip install -r requirements.txt`)
3. Run `alembic upgrade head` to apply all migrations
4. Start `uvicorn` on `$PORT`

The app includes a `/health` endpoint for Render's health checks:

```json
{"status": "healthy", "service": "AgriBrain AI", "version": "1.0.0"}
```

---

## 6. Verify Deployment

```bash
# Health check
curl https://agribrain-ai-api.onrender.com/health

# API docs
curl https://agribrain-ai-api.onrender.com/docs

# Root
curl https://agribrain-ai-api.onrender.com/
```

---

## 7. Database Migrations

Migrations are defined in `alembic/versions/`:

| Migration | Description |
|---|---|
| `001_initial_migration.py` | All core tables (users, farms, fields, crops, etc.) |
| `002_add_missing_tables.py` | disease_detections, whatsapp_sessions, notification_logs, reminder_preferences |

The alembic config automatically picks up `DATABASE_URL` from the environment.

---

## 8. Troubleshooting

### 8.1 Deployment fails with "Connection refused"
- Check Neon's IP allowlist. Add `0.0.0.0/0` (allow all) or Render's IP range.
- Verify `DATABASE_URL` is correct in Render env vars.

### 8.2 Migration fails with "relation already exists"
- This means tables already exist. Run the following in a Render shell:
  ```bash
  alembic upgrade head
  ```
  If it still fails, stamp manually:
  ```bash
  alembic stamp head
  ```

### 8.3 App starts but /health returns 500
- Check Render logs for traceback.
- Common cause: missing `SECRET_KEY` or `DATABASE_URL`.

### 8.4 asyncpg SSL errors
- The app converts `sslmode=require` to `ssl=true` automatically. If you see SSL errors, verify your `DATABASE_URL` uses `postgresql://` (not `postgresql+asyncpg://`).

### 8.5 Free tier cold start
- The free Render tier spins down after inactivity. First request after idle period may take 30-60 seconds.

---

## 9. Local Testing with Production Settings

To test production DB connection locally:

```bash
# Temporarily remove .env so DATABASE_URL env var is used
cd backend
mv .env .env.local
# Set DATABASE_URL in your environment
$env:DATABASE_URL="postgresql://..."
uvicorn app.main:app --reload
# Restore .env
mv .env.local .env
```

Or add `DATABASE_URL` to `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/agribrain
```
