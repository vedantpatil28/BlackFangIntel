#!/usr/bin/env python3
"""
BlackFang Intelligence - ULTRA-SIMPLIFIED VERSION
This WILL work on Railway without ANY dependency conflicts
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from datetime import datetime

# Initialize FastAPI
app = FastAPI(title="BlackFang Intelligence", version="2.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {
        "message": "🎯 BlackFang Intelligence API v2.0",
        "status": "operational",
        "demo_url": "/app",
        "health_check": "/health"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "demo_mode"
    }

@app.post("/api/auth/login")
async def login(email: str = Form(...), password: str = Form(...)):
    if email == 'demo@blackfangintel.com' and password == 'demo123':
        return {
            "success": True,
            "user": {
                "id": 1,
                "name": "Demo Automotive Dealership",
                "email": email,
                "company_name": "Demo Motors Pvt Ltd"
            }
        }
    else:
        return {"success": False, "error": "Invalid credentials"}

@app.get("/api/dashboard/{company_id}")
async def get_dashboard_data(company_id: int):
    return {
        "statistics": {
            "competitors": 3,
            "alerts": 8,
            "high_priority_alerts": 2,
            "monitoring_status": "24/7 Active"
        },
        "recent_alerts": [
            {
                "id": 1,
                "title": "🔴 CRITICAL: Price War Detected - AutoMax Dealers",
                "severity": "HIGH", 
                "message": "AutoMax Dealers implemented aggressive 8% price reduction on Honda City models (₹95,000 decrease). Market share impact imminent.",
                "recommendation": "IMMEDIATE ACTION: Consider price matching or launch Premium Service Value campaign.",
                "competitor_name": "AutoMax Dealers",
                "confidence_score": 0.95,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": 2,
                "title": "🟡 ALERT: Marketing Campaign - Speed Motors",
                "severity": "MEDIUM",
                "message": "Speed Motors launched Monsoon Festival Special: 5% discount + Free insurance + Extended warranty.",
                "recommendation": "STRATEGIC RESPONSE: Deploy counter-campaign within 72 hours.",
                "competitor_name": "Speed Motors", 
                "confidence_score": 0.87,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": 3,
                "title": "🟡 OPPORTUNITY: Service Issues - Elite Auto",
                "severity": "MEDIUM",
                "message": "Elite Auto received 4 negative reviews citing delivery delays and poor support.",
                "recommendation": "MARKET OPPORTUNITY: Launch Satisfaction Guarantee campaign.",
                "competitor_name": "Elite Auto Solutions",
                "confidence_score": 0.91,
                "created_at": datetime.utcnow().isoformat()
            }
        ],
        "competitors": [
            {
                "id": 1,
                "name": "AutoMax Dealers",
                "website": "cars24.com",
                "threat_level": "HIGH",
                "alert_count": 3,
                "monitoring_status": "active"
            },
            {
                "id": 2, 
                "name": "Speed Motors",
                "website": "carwale.com", 
                "threat_level": "MEDIUM",
                "alert_count": 2,
                "monitoring_status": "active"
            },
            {
                "id": 3,
                "name": "Elite Auto Solutions",
                "website": "cardekho.com",
                "threat_level": "LOW", 
                "alert_count": 3,
                "monitoring_status": "active"
            }
        ]
    }

@app.get("/app", response_class=HTMLResponse)
async def serve_login():
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
            
            <div class="demo-info">
                <h3>🎯 Demo Account Access</h3>
                <p><strong>Email:</strong> demo@blackfangintel.com</p>
                <p><strong>Password:</strong> demo123</p>
                <p>Experience complete competitive intelligence with real-time monitoring, threat detection, and strategic recommendations.</p>
            </div>
        </div>
        
        <script>
            function showError(message) {
                const error = document.getElementById('error');
                error.textContent = message;
                error.style.display = 'block';
                setTimeout(() => error.style.display = 'none', 5000);
            }
            
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const email = document.getElementById('email').value.trim();
                const password = document.getElementById('password').value;
                
                if (!email || !password) {
                    showError('Please enter both email and password');
                    return;
                }
                
                try {
                    const formData = new FormData();
                    formData.append('email', email);
                    formData.append('password', password);
                    
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        window.location.href = `/dashboard/${data.user.id}`;
                    } else {
                        showError(data.error || 'Login failed');
                    }
                } catch (error) {
                    showError('Connection error. Please try again.');
                }
            });
        </script>
    </body>
    </html>
    """

@app.get("/dashboard/{company_id}", response_class=HTMLResponse)
async def serve_dashboard(company_id: int):
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
            .refresh-btn {{
                background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 10px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
                margin-bottom: 32px;
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
            <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Intelligence Data</button>
            
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
                    <div class="alert-message">AutoMax Dealers implemented aggressive 8% price reduction on Honda City models (₹95,000 decrease). Market share impact imminent within 48 hours. Competitive analysis shows this is part of Q4 market expansion strategy.</div>
                    <div class="alert-recommendation"><strong>Strategic Response:</strong> IMMEDIATE ACTION: Consider price matching within 24 hours, OR launch "Premium Service Value" campaign highlighting superior warranty and customer support. Activate loyalty program for existing customers.</div>
                </div>
                
                <div class="alert">
                    <div class="alert-title">🟡 STRATEGIC ALERT: Comprehensive Marketing Campaign - Speed Motors</div>
                    <div class="alert-message">Speed Motors launched multi-channel "Monsoon Festival Special" campaign: 5% additional discount + Free comprehensive insurance + Extended warranty + Zero processing fees. Digital ad spend increased 40%.</div>
                    <div class="alert-recommendation"><strong>Strategic Response:</strong> Deploy "Exclusive Client Benefits" package within 72 hours with comparable value proposition. Leverage social media with customer testimonials and activate email marketing to warm leads.</div>
                </div>
                
                <div class="alert">
                    <div class="alert-title">🟡 MARKET OPPORTUNITY: Service Quality Issues - Elite Auto</div>
                    <div class="alert-message">Elite Auto Solutions received 4 negative reviews in past 48 hours citing delivery delays, poor after-sales support, and parts availability issues. Customer sentiment analysis shows -15% decline.</div>
                    <div class="alert-recommendation"><strong>Competitive Advantage:</strong> Launch "Guaranteed Delivery Timeline" campaign with penalty clause. Target their dissatisfied customers with "Satisfaction Guarantee" program and superior service messaging.</div>
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
                // Simulate real-time data refresh
                const alerts = document.querySelectorAll('.alert-title');
                alerts.forEach((alert, index) => {{
                    setTimeout(() => {{
                        alert.style.animation = 'pulse 0.5s ease-in-out';
                        setTimeout(() => alert.style.animation = '', 500);
                    }}, index * 200);
                }});
                
                // Update status
                const statusText = document.querySelector('.status span');
                statusText.textContent = 'Data Refreshed - ' + new Date().toLocaleTimeString();
                setTimeout(() => {{
                    statusText.textContent = 'Live Monitoring Active';
                }}, 3000);
            }}
            
            // Auto-refresh every 30 seconds (demo)
            setInterval(() => {{
                console.log('Auto-refresh: BlackFang Intelligence monitoring active');
            }}, 30000);
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)