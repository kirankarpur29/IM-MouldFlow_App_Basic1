"""
MouldFlow Analysis API - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, async_session
from app.seed_data import seed_database
from app.api.v1 import materials, machines, projects, parts, analysis, reports

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    async with async_session() as session:
        await seed_database(session)
    yield
    # Shutdown
    pass

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Open-source mold flow analysis for injection molding feasibility assessment",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(materials.router, prefix="/api/v1/materials", tags=["Materials"])
app.include_router(machines.router, prefix="/api/v1/machines", tags=["Machines"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(parts.router, prefix="/api/v1/parts", tags=["Parts"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
