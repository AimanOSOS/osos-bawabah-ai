from fastapi import FastAPI
from .routers import tts, rerank, ocr

app = FastAPI(
    title="Bawabah AI",
    description="An API server for various machine learning models.",
    version="1.0.0",
)

# Include the routers from the routers module
app.include_router(tts.router, prefix="/api/v1")
app.include_router(rerank.router)
app.include_router(ocr.router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
async def read_root():
    return {"message": "Welcome to Bawabah AI"}