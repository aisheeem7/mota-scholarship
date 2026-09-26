from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.admin import router as admin_router
from app.api.routes.applications import router as applications_router


app = FastAPI(
    title="MoTA Scholarship Management API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    applications_router,
    prefix="/api/v1/applications",
    tags=["Applications"],
)


app.include_router(
    admin_router,
    prefix="/api/v1/admin",
    tags=["Admin"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "mota-scholarship-api",
    }