from fastapi import FastAPI

from .routers import reports, channels, search

app = FastAPI(
    title="Medical Telegram Analytics API",
    description="Analytical API for Telegram-based medical market insights",
    version="1.0.0",
)

app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(channels.router, prefix="/api/channels", tags=["Channels"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])


@app.get("/")
def root():
    return {
        "service": "Medical Telegram Analytics API",
        "status": "running",
        "docs": "/docs"
    }
