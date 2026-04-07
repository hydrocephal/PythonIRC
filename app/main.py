import asyncio
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.core.config import settings
from app.db.database import engine
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.services.chat import listen_pubsub

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[
        FastApiIntegration(),
        AsyncioIntegration(),
    ],
    traces_sample_rate=1.0,  # 100% traces
    send_default_pii=False,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(listen_pubsub())
    yield
    task.cancel()
    await engine.dispose()


app = FastAPI(title="Ghost IRC Chat", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(chat_router)

Instrumentator().instrument(app).expose(app)


@app.get("/")
def read_root():
    return {"message": "Welcome to Ghost IRC Chat"}
