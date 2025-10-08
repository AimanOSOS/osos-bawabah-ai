from fastapi import FastAPI
from .routers import tts, itx

# Create FastAPI app only once
app = FastAPI(
    title="Bawabah AI",
    description="An API server for various machine learning models.",
    version="1.0.0",
)

# Register routers
app.include_router(tts.router, prefix="/api/v1")
app.include_router(itx.router, prefix="/api/v1")


# Health check route
@app.get("/", tags=["Health Check"])
async def read_root():
    return {"message": "Welcome to Bawabah AI"}
