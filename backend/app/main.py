from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_db_and_tables
from .brokers.routes import router as broker_router
from .strategies.routes import router as strategy_router
from .execution.routes import router as execution_router
from .management.routes import router as management_router
from .validation.routes import router as validation_router
from .alerts.routes import router as alert_router
from .analytics.routes import router as analytics_router
from .system.routes import router as system_router
import asyncio
from .scheduler.task_loop import scheduler
from .management.management_loop import management_loop

app = FastAPI(title="Trading Workstation API")

@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(scheduler.start())
    asyncio.create_task(management_loop.start())

app.include_router(broker_router)
app.include_router(alert_router)
app.include_router(system_router)
app.include_router(strategy_router)
app.include_router(analytics_router)
app.include_router(execution_router)
app.include_router(management_router)
app.include_router(validation_router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Trading Workstation API is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}
