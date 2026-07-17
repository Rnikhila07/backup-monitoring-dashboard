from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, dashboard, auth

app = FastAPI(title="Enterprise Backup Monitoring Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(dashboard.router)
app.include_router(auth.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}