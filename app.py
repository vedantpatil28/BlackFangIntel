#!/usr/bin/env python3
"""
BlackFang Intelligence - Main Application
Complete competitive intelligence platform for SMBs
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Local imports
from database import init_database, close_database
from models import *
from config import settings
from api.auth import auth_router
from api.dashboard import dashboard_router  
from api.competitors import competitors_router
from api.alerts import alerts_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("🚀 Starting BlackFang Intelligence Platform...")
    
    try:
        # Initialize database
        await init_database()
        logger.info("✅ Database initialized successfully")
        
        logger.info("🎯 BlackFang Intelligence is OPERATIONAL")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        if settings.ENVIRONMENT == "production":
            raise
        else:
            logger.warning("⚠️ Running in development mode without database")
    
    yield
    
    # Cleanup
    try:
        await close_database()
        logger.info("🗄️ Database connections closed")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

# Initialize FastAPI application
app = FastAPI(
    title="BlackFang Intelligence",
    description="Professional Competitive Intelligence Platform for SMBs",
    version="2.0.0",
    docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Configure middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include API routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(competitors_router, prefix="/api/competitors", tags=["Competitors"])
app.include_router(alerts_router, prefix="/api/alerts", tags=["Alerts"])

# Main routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Landing page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "BlackFang Intelligence",
        "version": "2.0.0"
    })

@app.get("/app", response_class=HTMLResponse)
async def login_page(request: Request):
    """Client login page"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "title": "Login - BlackFang Intelligence"
    })

@app.get("/dashboard/{company_id}", response_class=HTMLResponse)
async def dashboard_page(company_id: int, request: Request):
    """Intelligence dashboard"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "company_id": company_id,
        "title": "Dashboard - BlackFang Intelligence"
    })

@app.get("/competitors", response_class=HTMLResponse)  
async def competitors_page(request: Request):
    """Competitor management page"""
    return templates.TemplateResponse("competitors.html", {
        "request": request,
        "title": "Competitors - BlackFang Intelligence"
    })

@app.get("/alerts", response_class=HTMLResponse)
async def alerts_page(request: Request):
    """Alerts management page"""
    return templates.TemplateResponse("alerts.html", {
        "request": request,
        "title": "Alerts - BlackFang Intelligence"
    })

@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Intelligence reports page"""
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "title": "Reports - BlackFang Intelligence"
    })

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """User settings page"""
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "title": "Settings - BlackFang Intelligence"
    })

@app.get("/health")
async def health_check():
    """System health check"""
    try:
        from database import db_pool
        health_status = {
            "status": "healthy",
            "version": "2.0.0",
            "environment": settings.ENVIRONMENT,
            "database": "connected" if db_pool else "offline"
        }
        
        if db_pool:
            async with db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "version": "2.0.0"
        }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.ENVIRONMENT == "development"
    )