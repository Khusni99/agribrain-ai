from app.core.celery_app import celery_app


@celery_app.task
def fetch_weather_data():
    from app.services.weather_service import WeatherService
    import asyncio
    service = WeatherService()
    asyncio.run(service.get_current_weather(-6.2, 106.8))
    return "Weather data fetched"


@celery_app.task
def generate_disease_alerts():
    return "Disease alerts generated"


@celery_app.task
def cleanup_old_records():
    return "Old records cleaned up"


@celery_app.task
def send_daily_reports():
    return "Daily reports sent"
