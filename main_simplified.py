#!/usr/bin/env python3
"""
BLACKFANG INTELLIGENCE - SIMPLIFIED PRODUCTION VERSION
Fixed for Railway deployment
"""

import os
import asyncio
import logging
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
DATABASE_URL = os.getenv('DATABASE_URL')
JWT_SECRET = os.getenv('JWT_SECRET', 'blackfang-production-key-2025')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')

# Global database pool
db_pool = None

class AuthManager:
    """Secure authentication management"""
    
    def __init__(self):
        self.secret_key = JWT_SECRET
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60

    def hash_password(self, password: str) -> str:
        """Hash password securely with salt"""
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hashed.hex() + ':' + salt

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            stored_hash, salt = hashed.split(':')
            computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return computed_hash.hex() == stored_hash
        except:
            return False

    def create_access_token(self, data: dict) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        """Decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

# Initialize database if available
async def init_database():
    """Initialize database if available"""
    if not DATABASE_URL:
        logger.info("No database URL - running in demo mode")
        return
        
    try:
        import asyncpg
        global db_pool
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
        logger.info("✅ Database connected")
        
        # Initialize schema
        async with db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    company_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create demo user
            auth = AuthManager()
            password_hash = auth.hash_password('demo123')
            
            await conn.execute("""
                INSERT INTO companies (name, email, password_hash, company_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (email) DO NOTHING
            """, 'Demo Company', 'demo@blackfangintel.com', password_hash, 'Demo Motors Pvt Ltd')
            
        logger.info("✅ Database initialized")
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        logger.info("Running in demo mode without database")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("🚀 Starting BlackFang Intelligence...")
    
    try:
        await init_database()
        logger.info("🎯 BlackFang Intelligence OPERATIONAL")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        logger.info("🎯 BlackFang Intelligence running in demo mode")
    
    yield
    
    if db_pool:
        await db_pool.close()

# Initialize FastAPI
app = FastAPI(
    title="BlackFang Intelligence",
    description="Professional Competitive Intelligence Platform",
    version="2.0.0",
    lifespan=lifespan
)

# Configure middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize components
auth_manager = AuthManager()
security = HTTPBearer()

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Authenticate current user"""
    try:
        payload = auth_manager.decode_token(credentials.credentials)
        company_id = payload.get("company_id")
        
        if not company_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Return demo user for now
        return {"id": company_id, "email": payload.get("email"), "name": "Demo Company"}
        
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Authentication failed")

# API Routes
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "🎯 BlackFang Intelligence API v2.0",
        "status": "operational",
        "version": "2.0.0",
        "environment": ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "demo_access": "/app"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }
    
    if db_pool:
        try:
            async with db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            health["database"] = "connected"
        except:
            health["database"] = "error"
    else:
        health["database"] = "demo_mode"
    
    return health

@app.post("/api/auth/login")
async def authenticate_user(request: Request):
    """User authentication endpoint"""
    try:
        data = await request.json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        
        # Demo authentication
        if email == 'demo@blackfangintel.com' and password == 'demo123':
            token_data = {"company_id": 1, "email": email}
            access_token = auth_manager.create_access_token(token_data)
            
            return {
                "success": True,
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": auth_manager.access_token_expire_minutes * 60,
                "user": {
                    "id": 1,
                    "name": "Demo Automotive Dealership",
                    "email": email,
                    "company_name": "Demo Motors Pvt Ltd",
                    "subscription_plan": "professional",
                    "monthly_fee": 45000
                }
            }
        
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@app.get("/api/dashboard/{company_id}")
async def get_dashboard_data(
    company_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard intelligence data"""
    if current_user['id'] != company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Return demo data
    return {
        "statistics": {
            "competitors": {
                "total_competitors": 3,
                "active_competitors": 3,
                "high_threat_count": 1,
                "medium_threat_count": 1,
                "low_threat_count": 1
            },
            "alerts": {
                "total_alerts": 8,
                "high_priority_alerts": 2,
                "medium_priority_alerts": 3,
                "low_priority_alerts": 3,
                "unread_alerts": 5,
                "today_alerts": 3,
                "week_alerts": 8
            }
        },
        "recent_alerts": [
            {
                "id": 1,
                "title": "🔴 CRITICAL: Major Price War Detected",
                "severity": "HIGH",
                "message": "AutoMax Dealers implemented aggressive 8% price reduction on Honda City models (₹95,000 decrease). Market share impact imminent within 48 hours.",
                "recommendation": "IMMEDIATE ACTION: Consider price matching strategy or launch Premium Service Value campaign highlighting superior customer service and warranty benefits.",
                "competitor_name": "AutoMax Dealers",
                "confidence_score": 0.95,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": 2,
                "title": "🟡 ALERT: Aggressive Marketing Campaign Launch",
                "severity": "MEDIUM",
                "message": "Speed Motors launched comprehensive Monsoon Festival Special campaign: 5% additional discount + Free comprehensive insurance + Extended warranty.",
                "recommendation": "STRATEGIC RESPONSE: Deploy counter-campaign within 72 hours. Consider Exclusive Client Benefits package with added-value services.",
                "competitor_name": "Speed Motors",
                "confidence_score": 0.87,
                "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat()
            },
            {
                "id": 3,
                "title": "🟡 OPPORTUNITY: Competitor Service Issues",
                "severity": "MEDIUM",
                "message": "Elite Auto Solutions received 4 negative reviews in past 48 hours citing delivery delays and poor after-sales support. Customer sentiment declining (-15%).",
                "recommendation": "MARKET OPPORTUNITY: Target messaging around Reliable Delivery & Premium Support. Launch Satisfaction Guarantee campaign to capture dissatisfied customers.",
                "competitor_name": "Elite Auto Solutions",
                "confidence_score": 0.91,
                "created_at": (datetime.utcnow() - timedelta(hours=5)).isoformat()
            }
        ],
        "competitors": [
            {
                "id": 1,
                "name": "AutoMax Dealers",
                "website": "https://cars24.com",
                "threat_level": "HIGH",
                "industry": "Automotive",
                "monitoring_status": "active",
                "alert_count": 3,
                "last_scraped": datetime.utcnow().isoformat()
            },
            {
                "id": 2,
                "name": "Speed Motors",
                "website": "https://carwale.com",
                "threat_level": "MEDIUM",
                "industry": "Automotive",
                "monitoring_status": "active",
                "alert_count": 2,
                "last_scraped": datetime.utcnow().isoformat()
            },
            {
                "id": 3,
                "name": "Elite Auto Solutions",
                "website": "https://cardekho.com",
                "threat_level": "LOW",
                "industry": "Automotive",
                "monitoring_status": "active",
                "alert_count": 3,
                "last_scraped": datetime.utcnow().isoformat()
            }
        ],
        "system_status": {
            "monitoring_active": True,
            "last_update": datetime.utcnow().isoformat(),
            "data_freshness": "real-time"
        }
    }

@app.get("/app", response_class=HTMLResponse)
async def serve_login_interface():
    """Professional client login interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BlackFang Intelligence - Professional Login</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
                color: #ffffff;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: linear-gradient(135deg, rgba(30, 30, 30, 0.95) 0%, rgba(42, 42, 42, 0.95) 100%);
                backdrop-filter: blur(20px);
                padding: 60px 50px;
                border-radius: 24px;
                box-shadow: 0 32px 64px rgba(0, 0, 0, 0.4);
                max-width: 480px;
                width: 100%;
                border-top: 4px solid #dc2626;
            }
            .brand {
                text-align: center;
                margin-bottom: 40px;
            }
            .brand h1 {
                font-size: 32px;
                font-weight: 800;
                background: linear-gradient(135deg, #dc2626 0%, #f59e0b 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 8px;
            }
            .brand p {
                color: #a0a0a0;
                font-size: 16px;
            }
            .form-group {
                margin-bottom: 24px;
            }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                color: #e5e5e5;
                font-weight: 600;
                font-size: 14px;
            }
            .form-group input {
                width: 100%;
                padding: 16px 20px;
                border: 2px solid rgba(255, 255, 255, 0.1);
                background: rgba(0, 0, 0, 0.3);
                color: #ffffff;
                border-radius: 12px;
                font-size: 16px;
                transition: all 0.3s ease;
            }
            .form-group input:focus {
                outline: none;
                border-color: #dc2626;
                background: rgba(0, 0, 0, 0.5);
                box-shadow: 0 0 0 4px rgba(220, 38, 38, 0.1);
            }
            .login-btn {
                width: 100%;
                padding: 18px 24px;
                background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
                border: none;
                border-radius: 12px;
                color: #ffffff;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .login-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 28px rgba(220, 38, 38, 0.4);
            }
            .demo-info {
                margin-top: 32px;
                padding: 24px;
                background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%);
                border-radius: 16px;
                border-left: 4px solid #dc2626;
            }
            .demo-info h3 {
                color: #dc2626;
                font-weight: 700;
                font-size: 18px;
                margin-bottom: 16px;
            }
            .demo-info p {
                margin-bottom: 12px;
                line-height: 1.6;
                color: #d0d0d0;
            }
            .demo-info strong {
                color: #ffffff;
                font-weight: 600;
            }
            .loading {
                display: none;
                text-align: center;
                margin-top: 24px;
            }
            .spinner {
                border: 3px solid rgba(255, 255, 255, 0.1);
                border-top: 3px solid #dc2626;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 16px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .error {
                background: rgba(220, 38, 38, 0.1);
                color: #dc2626;
                padding: 16px;
                border-radius: 12px;
                margin-bottom: 24px;
                display: none;
            }
            @media (max-width: 640px) {
                .container { padding: 40px 30px; margin: 20px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="brand">
                <h1>⚡ BLACKFANG INTELLIGENCE</h1>
                <p>Professional Competitive Intelligence Platform</p>
            </div>
            
            <div id="error" class="error"></div>
            
            <form id="loginForm">
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" value="demo@blackfangintel.com" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" value="demo123" required>
                </div>
                <button type="submit" class="login-btn">Access Intelligence Dashboard</button>
            </form>
            
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>Authenticating and preparing dashboard...</p>
            </div>
            
            <div class="demo-info">
                <h3>🎯 Demo Account Access</h3>
                <p><strong>Email:</strong> demo@blackfangintel.com</p>
                <p><strong>Password:</strong> demo123</p>
                <p>Experience the complete competitive intelligence platform with real-time monitoring, threat detection, and strategic recommendations for automotive dealerships.</p>
            </div>
        </div>
        
        <script>
            function showError(message) {
                const error = document.getElementById('error');
                error.textContent = message;
                error.style.display = 'block';
                setTimeout(() => error.style.display = 'none', 5000);
            }
            
            function showLoading(show) {
                const form = document.getElementById('loginForm');
                const loading = document.getElementById('loading');
                form.style.display = show ? 'none' : 'block';
                loading.style.display = show ? 'block' : 'none';
            }
            
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const email = document.getElementById('email').value.trim();
                const password = document.getElementById('password').value;
                
                if (!email || !password) {
                    showError('Please enter both email and password');
                    return;
                }
                
                showLoading(true);
                
                try {
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        localStorage.setItem('blackfang_access_token', data.access_token);
                        localStorage.setItem('blackfang_user_data', JSON.stringify(data.user));
                        window.location.href = `/dashboard/${data.user.id}`;
                    } else {
                        showError(data.detail || 'Login failed');
                        showLoading(false);
                    }
                } catch (error) {
                    showError('Connection error. Please try again.');
                    showLoading(false);
                }
            });
        </script>
    </body>
    </html>
    """

@app.get("/dashboard/{company_id}", response_class=HTMLResponse)
async def serve_dashboard(company_id: int):
    """Professional intelligence dashboard"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BlackFang Intelligence - Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
                color: #ffffff;
                min-height: 100vh;
            }}
            .header {{
                background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
                padding: 20px 0;
                border-bottom: 1px solid rgba(220, 38, 38, 0.3);
                position: sticky;
                top: 0;
                z-index: 1000;
            }}
            .header-content {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 24px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .brand {{
                font-size: 24px;
                font-weight: 800;
                background: linear-gradient(135deg, #dc2626 0%, #f59e0b 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .status {{
                display: flex;
                align-items: center;
                gap: 12px;
                color: #a0a0a0;
            }}
            .status-dot {{
                width: 8px;
                height: 8px;
                background: #10b981;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 32px 24px;
            }}
            .controls {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 32px;
                padding: 20px 24px;
                background: rgba(30, 30, 30, 0.8);
                border-radius: 16px;
            }}
            .refresh-btn {{
                background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 10px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
            }}
            .refresh-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(220, 38, 38, 0.4);
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 24px;
                margin-bottom: 40px;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
                padding: 32px 28px;
                border-radius: 20px;
                border-left: 6px solid #dc2626;
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
                transition: all 0.4s ease;
            }}
            .stat-card:hover {{
                transform: translateY(-8px);
                box-shadow: 0 20px 40px rgba(220, 38, 38, 0.2);
            }}
            .stat-number {{
                font-size: 48px;
                font-weight: 900;
                background: linear-gradient(135deg, #dc2626 0%, #f59e0b 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 8px;
            }}
            .stat-label {{
                color: #d0d0d0;
                font-size: 16px;
                font-weight: 600;
            }}
            .section {{
                background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
                padding: 36px 32px;
                border-radius: 20px;
                margin-bottom: 32px;
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
            }}
            .section-title {{
                font-size: 24px;
                font-weight: 800;
                background: linear-gradient(135deg, #dc2626 0%, #f59e0b 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 28px;
            }}
            .alert {{
                background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%);
                padding: 28px 24px;
                margin: 20px 0;
                border-radius: 16px;
                border-left: 6px solid #dc2626;
                transition: all 0.3s ease;
            }}
            .alert:hover {{
                transform: translateX(12px);
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
            }}
            .alert-title {{
                font-size: 20px;
                font-weight: 800;
                color: #ffffff;
                margin-bottom: 16px;
            }}
            .alert-message {{
                color: #e5e5e5;
                line-height: 1.7;
                margin-bottom: 16px;
            }}
            .alert-recommendation {{
                background: rgba(0, 0, 0, 0.4);
                padding: 18px 20px;
                border-radius: 12px;
                border-left: 4px solid #dc2626;
                color: #d0d0d0;
                line-height: 1.6;
            }}
            .competitor {{
                background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%);
                padding: 28px 24px;
                margin: 20px 0;
                border-radius: 16px;
                border-left: 6px solid #666;
                transition: all 0.3s ease;
            }}
            .competitor:hover {{
                transform: translateX(12px);
                border-left-color: #dc2626;
            }}
            .competitor-name {{
                font-size: 22px;
                font-weight: 800;
                color: #ffffff;
                margin-bottom: 16px;
            }}
            .threat-level {{
                display: inline-block;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                margin-bottom: 16px;
            }}
            .threat-level.high {{
                background: rgba(220, 38, 38, 0.2);
                color: #dc2626;
            }}
            .threat-level.medium {{
                background: rgba(245, 158, 11, 0.2);
                color: #f59e0b;
            }}
            .threat-level.low {{
                background: rgba(16, 185, 129, 0.2);
                color: #10b981;
            }}
            @media (max-width: 768px) {{
                .container {{ padding: 20px 16px; }}
                .stats-grid {{ grid-template-columns: 1fr; }}
                .controls {{ flex-direction: column; gap: 16px; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <div class="brand">⚡ BLACKFANG INTELLIGENCE</div>
                <div class="status">
                    <div class="status-dot"></div>
                    <span>Live Monitoring Active</span>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="controls">
                <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Intelligence Data</button>
                <div style="color: #888;">Last updated: <span id="lastUpdated">Just now</span></div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">3</div>
                    <div class="stat-label">Competitors Monitored</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">8</div>
                    <div class="stat-label">Active Threat Alerts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">2</div>
                    <div class="stat-label">High Priority Threats</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">24/7</div>
                    <div class="stat-label">Real-time Intelligence</div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">🚨 Critical Threat Intelligence</div>
                
                <div class="alert">
                    <div class="alert-title">🔴 CRITICAL: Major Price War Detected - AutoMax Dealers</div>
                    <div class="alert-message">AutoMax Dealers implemented aggressive 8% price reduction on Honda City models (₹95,000 decrease). Market share impact imminent within 48 hours.</div>
                    <div class="alert-recommendation"><strong>Strategic Response:</strong> IMMEDIATE ACTION: Consider price matching strategy or launch Premium Service Value campaign highlighting superior customer service and warranty benefits.</div>
                </div>
                
                <div class="alert">
                    <div class="alert-title">🟡 ALERT: Aggressive Marketing Campaign - Speed Motors</div>
                    <div class="alert-message">Speed Motors launched comprehensive Monsoon Festival Special campaign: 5% additional discount + Free comprehensive insurance + Extended warranty.</div>
                    <div class="alert-recommendation"><strong>Strategic Response:</strong> Deploy counter-campaign within 72 hours. Consider Exclusive Client Benefits package with added-value services.</div>
                </div>
                
                <div class="alert">
                    <div class="alert-title">🟡 OPPORTUNITY: Competitor Service Issues - Elite Auto</div>
                    <div class="alert-message">Elite Auto Solutions received 4 negative reviews in past 48 hours citing delivery delays and poor after-sales support.</div>
                    <div class="alert-recommendation"><strong>Market Opportunity:</strong> Target messaging around Reliable Delivery & Premium Support. Launch Satisfaction Guarantee campaign.</div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">👥 Competitor Intelligence Network</div>
                
                <div class="competitor">
                    <div class="competitor-name">🎯 AutoMax Dealers</div>
                    <div class="threat-level high">HIGH THREAT</div>
                    <p><strong>Website:</strong> cars24.com | <strong>Industry:</strong> Automotive</p>
                    <p><strong>Intelligence Analysis:</strong> Aggressive pricing strategy detected. 8% price reduction on premium models targeting market share expansion through competitive pricing.</p>
                </div>
                
                <div class="competitor">
                    <div class="competitor-name">⚡ Speed Motors</div>
                    <div class="threat-level medium">MEDIUM THREAT</div>
                    <p><strong>Website:</strong> carwale.com | <strong>Industry:</strong> Automotive</p>
                    <p><strong>Intelligence Analysis:</strong> Promotional focus with seasonal campaigns. Moderate pricing adjustments and strong digital marketing presence across multiple channels.</p>
                </div>
                
                <div class="competitor">
                    <div class="competitor-name">🚗 Elite Auto Solutions</div>
                    <div class="threat-level low">LOW THREAT</div>
                    <p><strong>Website:</strong> cardekho.com | <strong>Industry:</strong> Automotive</p>
                    <p><strong>Intelligence Analysis:</strong> Service quality issues emerging. Customer complaints about delivery delays present competitive opportunity for superior service positioning.</p>
                </div>
            </div>
        </div>
        
        <script>
            function refreshData() {{
                document.getElementById('lastUpdated').textContent = new Date().toLocaleTimeString();
                // In real implementation, this would fetch fresh data from API
            }}
            
            // Auto-refresh every 30 seconds
            setInterval(() => {{
                document.getElementById('lastUpdated').textContent = new Date().toLocaleTimeString();
            }}, 30000);
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)