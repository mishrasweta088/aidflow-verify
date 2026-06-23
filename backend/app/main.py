from fastapi import FastAPI

from app.api.auth import router as auth_router

app = FastAPI(
    title="AidFlow Verify API",
    description="Backend API for verified aid requests, AI review, volunteer verification, donor claims, and fulfillment tracking.",
    version="0.1.0",
)

app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"message": "AidFlow Verify API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
