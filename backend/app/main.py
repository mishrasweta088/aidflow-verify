from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.aid_requests import router as aid_requests_router

from app.api.verification_tasks import router as verification_tasks_router

from app.api.audit_logs import router as audit_logs_router

app = FastAPI(
    title="AidFlow Verify API",
    description="Backend API for verified aid requests, AI review, volunteer verification, donor claims, and fulfillment tracking.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://aidflow-verify.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(aid_requests_router)
app.include_router(verification_tasks_router)
app.include_router(audit_logs_router)



@app.get("/")
def read_root():
    return {"message": "AidFlow Verify API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
