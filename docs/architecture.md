# AgriBrain AI Architecture

## System Overview

```
┌─────────────────────────────────────────────────────┐
│                   Flutter Frontend                   │
│            (Mobile + Web Dashboard)                  │
└─────────────────────┬───────────────────────────────┘
                      │ HTTPS/REST
┌─────────────────────▼───────────────────────────────┐
│                 FastAPI Backend                       │
│  ┌──────────┐ ┌──────────┐ ┌────────────────────┐   │
│  │ Auth API │ │ Farm API │ │ Diagnosis API      │   │
│  └──────────┘ └──────────┘ └────────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌────────────────────┐   │
│  │Weather API│ │Cost API  │ │ Marketplace API    │   │
│  └──────────┘ └──────────┘ └────────────────────┘   │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                  AI Layer                            │
│  ┌────────────────┐  ┌────────────────────────┐    │
│  │ LangGraph Agent │  │  Computer Vision       │    │
│  │ (Agronomist)    │  │  (YOLO + PyTorch)      │    │
│  └────────────────┘  └────────────────────────┘    │
│  ┌────────────────┐  ┌────────────────────────┐    │
│  │ RAG / Vector DB│  │  Recommendation Engine │    │
│  └────────────────┘  └────────────────────────┘    │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                 Data Layer                           │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │ PostgreSQL  │  │   Redis    │  │  Object Store│  │
│  └────────────┘  └────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Key Components

1. **FastAPI Backend** - REST API server with async support
2. **AI Agronomist Agent** - LangGraph-based agricultural expert system
3. **Computer Vision Module** - YOLO-based disease detection from plant images
4. **Weather Engine** - Real-time weather monitoring and disease risk prediction
5. **Cost Calculator** - Production cost analysis and ROI calculation
6. **Fertilizer Engine** - Smart NPK recommendation based on growth stage
7. **Spray Planner** - Resistance management and schedule optimization

## Data Flow

1. User submits query or image via Flutter app
2. FastAPI handles authentication and routing
3. AI Agent processes queries using LLM + domain knowledge
4. CV module processes images for disease detection
5. Results stored in PostgreSQL, cached in Redis
6. Celery handles background tasks (weather fetch, alerts)
7. Real-time notifications pushed to frontend
