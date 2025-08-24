# Dashboard and Client Management API Endpoints

@app.get("/api/dashboard/{company_id}")
async def get_dashboard_data(
    company_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive dashboard data"""
    if current_user['id'] != company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    async with db_pool.acquire() as conn:
        # Get company info
        company = await conn.fetchrow(
            "SELECT * FROM companies WHERE id = $1", company_id
        )
        
        # Get competitor count and status
        competitors_stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_competitors,
                COUNT(*) FILTER (WHERE monitoring_status = 'active') as active_competitors,
                COUNT(*) FILTER (WHERE threat_level = 'HIGH') as high_threat,
                COUNT(*) FILTER (WHERE threat_level = 'MEDIUM') as medium_threat,
                COUNT(*) FILTER (WHERE threat_level = 'LOW') as low_threat
            FROM competitors WHERE company_id = $1
        """, company_id)
        
        # Get recent alerts
        recent_alerts = await conn.fetch("""
            SELECT a.*, c.name as competitor_name
            FROM alerts a
            LEFT JOIN competitors c ON a.competitor_id = c.id
            WHERE a.company_id = $1 
            ORDER BY a.created_at DESC 
            LIMIT 20
        """, company_id)
        
        # Get alert summary
        alert_summary = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_alerts,
                COUNT(*) FILTER (WHERE severity = 'CRITICAL') as critical_alerts,
                COUNT(*) FILTER (WHERE severity = 'HIGH') as high_alerts,
                COUNT(*) FILTER (WHERE severity = 'MEDIUM') as medium_alerts,
                COUNT(*) FILTER (WHERE severity = 'LOW') as low_alerts,
                COUNT(*) FILTER (WHERE is_read = FALSE) as unread_alerts,
                COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE) as today_alerts,
                COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '7 days') as week_alerts
            FROM alerts WHERE company_id = $1
        """, company_id)
        
        # Get recent scraping activity
        recent_scraping = await conn.fetch("""
            SELECT 
                cd.scraped_at,
                cd.processing_status,
                c.name as competitor_name,
                c.website,
                c.threat_level
            FROM competitor_data cd
            JOIN competitors c ON cd.competitor_id = c.id
            WHERE c.company_id = $1
            ORDER BY cd.scraped_at DESC
            LIMIT 10
        """, company_id)
        
        # Get system performance metrics
        performance_stats = await conn.fetchrow("""
            SELECT 
                AVG(CASE WHEN cd.processing_status = 'completed' THEN 1.0 ELSE 0.0 END) as success_rate,
                COUNT(*) as total_scraping_jobs,
                COUNT(*) FILTER (WHERE cd.scraped_at >= CURRENT_DATE) as today_jobs
            FROM competitor_data cd
            JOIN competitors c ON cd.competitor_id = c.id
            WHERE c.company_id = $1 AND cd.scraped_at >= CURRENT_DATE - INTERVAL '30 days'
        """, company_id)
        
        return {
            "company": dict(company) if company else None,
            "competitors": dict(competitors_stats) if competitors_stats else {},
            "alerts": {
                "recent": [dict(alert) for alert in recent_alerts],
                "summary": dict(alert_summary) if alert_summary else {}
            },
            "scraping_activity": [dict(activity) for activity in recent_scraping],
            "performance": dict(performance_stats) if performance_stats else {},
            "last_updated": datetime.utcnow().isoformat()
        }

@app.get("/api/competitors/{company_id}")
async def get_competitors(
    company_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get all competitors for a company"""
    if current_user['id'] != company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    async with db_pool.acquire() as conn:
        competitors = await conn.fetch("""
            SELECT 
                c.*,
                COUNT(cd.id) as scraping_count,
                MAX(cd.scraped_at) as last_scraped,
                COUNT(a.id) as alert_count,
                COUNT(CASE WHEN a.severity IN ('HIGH', 'CRITICAL') THEN 1 END) as high_alerts
            FROM competitors c
            LEFT JOIN competitor_data cd ON c.id = cd.competitor_id
            LEFT JOIN alerts a ON c.id = a.competitor_id
            WHERE c.company_id = $1
            GROUP BY c.id
            ORDER BY c.priority ASC, c.threat_level DESC, c.created_at DESC
        """, company_id)
        
        return {
            "competitors": [dict(comp) for comp in competitors],
            "total": len(competitors),
            "active": len([c for c in competitors if c['monitoring_status'] == 'active'])
        }

@app.post("/api/competitors/{company_id}")
async def add_competitor(
    company_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Add new competitor for monitoring"""
    if current_user['id'] != company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        data = await request.json()
        
        required_fields = ['name', 'website']
        for field in required_fields:
            if not data.get(field):
                raise HTTPException(status_code=400, detail=f"Field '{field}' is required")
        
        # Validate website URL
        website = data['website'].strip()
        if not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        
        async with db_pool.acquire() as conn:
            # Check if competitor already exists
            existing = await conn.fetchrow(
                "SELECT id FROM competitors WHERE company_id = $1 AND website = $2",
                company_id, website
            )
            if existing:
                raise HTTPException(status_code=400, detail="Competitor already exists")
            
            # Check subscription limits
            current_count = await conn.fetchval(
                "SELECT COUNT(*) FROM competitors WHERE company_id = $1 AND monitoring_status = 'active'",
                company_id
            )
            
            # Get subscription plan limits
            company = await conn.fetchrow("SELECT subscription_plan FROM companies WHERE id = $1", company_id)
            plan_limits = {
                'basic': 5,
                'professional': 15,
                'enterprise': 999999
            }
            
            if current_count >= plan_limits.get(company['subscription_plan'], 5):
                raise HTTPException(status_code=400, detail="Competitor limit reached for your subscription plan")
            
            # Insert new competitor
            competitor_id = await conn.fetchval("""
                INSERT INTO competitors (
                    company_id, name, website, industry, location,
                    threat_level, priority, monitoring_status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """,
                company_id,
                data['name'].strip(),
                website,
                data.get('industry', ''),
                data.get('location', ''),
                data.get('threat_level', 'MEDIUM'),
                data.get('priority', 1),
                'active'
            )
            
            # Start initial scraping in background
            background_tasks.add_task(initial_competitor_scraping, competitor_id)
            
            return {
                "success": True,
                "competitor_id": competitor_id,
                "message": "Competitor added successfully"
            }
            
    except Exception as e:
        logger.error(f"Add competitor error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add competitor")

@app.get("/api/alerts/{company_id}")
async def get_alerts(
    company_id: int,
    severity: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get alerts with filtering and pagination"""
    if current_user['id'] != company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    async with db_pool.acquire() as conn:
        # Build query with filters
        where_clause = "WHERE a.company_id = $1"
        params = [company_id]
        
        if severity:
            where_clause += " AND a.severity = $2"
            params.append(severity.upper())
        
        query = f"""
            SELECT 
                a.*,
                c.name as competitor_name,
                c.website as competitor_website
            FROM alerts a
            LEFT JOIN competitors c ON a.competitor_id = c.id
            {where_clause}
            ORDER BY a.created_at DESC
            LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
        """
        params.extend([limit, offset])
        
        alerts = await conn.fetch(query, *params)
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM alerts a {where_clause}"
        total = await conn.fetchval(count_query, *params[:-2])
        
        return {
            "alerts": [dict(alert) for alert in alerts],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }

@app.post("/api/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Mark alert as read"""
    async with db_pool.acquire() as conn:
        # Verify alert belongs to user
        alert = await conn.fetchrow(
            "SELECT company_id FROM alerts WHERE id = $1",
            alert_id
        )
        
        if not alert or alert['company_id'] != current_user['id']:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Mark as read
        await conn.execute(
            "UPDATE alerts SET is_read = TRUE WHERE id = $1",
            alert_id
        )
        
        return {"success": True, "message": "Alert marked as read"}

@app.get("/api/reports/{company_id}")
async def get_reports(
    company_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get company reports"""
    if current_user['id'] != company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    async with db_pool.acquire() as conn:
        reports = await conn.fetch("""
            SELECT 
                id, title, report_type, generated_at, 
                file_size, download_count, email_sent
            FROM reports 
            WHERE company_id = $1 
            ORDER BY generated_at DESC 
            LIMIT 20
        """, company_id)
        
        return {
            "reports": [dict(report) for report in reports]
        }

@app.post("/api/reports/{company_id}/generate")
async def generate_report(
    company_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Generate new intelligence report"""
    if current_user['id'] != company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        data = await request.json()
        report_type = data.get('report_type', 'weekly')
        
        # Start report generation in background
        background_tasks.add_task(generate_intelligence_report, company_id, report_type)
        
        return {
            "success": True,
            "message": "Report generation started"
        }
        
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

# Professional Client Dashboard
@app.get("/app", response_class=HTMLResponse)
async def serve_application():
    """Serve the main client application"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BlackFang Intelligence - Login</title>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 50%, #0c0c0c 100%);
                color: #ffffff;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow-x: hidden;
            }
            
            .container {
                max-width: 1400px;
                width: 100%;
                padding: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .login-card {
                background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
                padding: 50px;
                border-radius: 20px;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.1);
                max-width: 500px;
                width: 100%;
                position: relative;
                overflow: hidden;
            }
            
            .login-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #dc2626, #f59e0b, #10b981, #3b82f6, #8b5cf6);
                border-radius: 20px 20px 0 0;
            }
            
            .brand {
                text-align: center;
                margin-bottom: 40px;
            }
            
            .brand h1 {
                font-size: 32px;
                font-weight: 700;
                background: linear-gradient(135deg, #dc2626 0%, #f59e0b 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 8px;
            }
            
            .brand p {
                color: #888;
                font-size: 16px;
                font-weight: 400;
            }
            
            .form-group {
                margin-bottom: 25px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 8px;
                color: #e5e5e5;
                font-weight: 500;
                font-size: 14px;
            }
            
            .form-group input {
                width: 100%;
                padding: 16px 20px;
                border: 2px solid #333;
                background: rgba(0, 0, 0, 0.3);
                color: #ffffff;
                border-radius: 12px;
                font-size: 16px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                backdrop-filter: blur(10px);
            }
            
            .form-group input:focus {
                outline: none;
                border-color: #dc2626;
                box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
                background: rgba(0, 0, 0, 0.5);
            }
            
            .login-btn {
                width: 100%;
                padding: 16px;
                background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }
            
            .login-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(220, 38, 38, 0.4);
            }
            
            .login-btn:active {
                transform: translateY(0);
            }
            
            .login-btn:disabled {
                opacity: 0.7;
                cursor: not-allowed;
                transform: none;
            }
            
            .demo-info {
                margin-top: 30px;
                padding: 20px;
                background: rgba(220, 38, 38, 0.1);
                border-radius: 12px;
                border-left: 4px solid #dc2626;
            }
            
            .demo-info h3 {
                color: #dc2626;
                margin-bottom: 12px;
                font-size: 18px;
            }
            
            .demo-info p {
                margin-bottom: 8px;
                line-height: 1.6;
                color: #ccc;
            }
            
            .loading {
                display: none;
                text-align: center;
                margin-top: 20px;
            }
            
            .spinner {
                border: 3px solid rgba(255, 255, 255, 0.1);
                border-top: 3px solid #dc2626;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 15px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .error-message {
                background: rgba(220, 38, 38, 0.1);
                color: #dc2626;
                padding: 12px 16px;
                border-radius: 8px;
                border-left: 4px solid #dc2626;
                margin-bottom: 20px;
                display: none;
            }
            
            @media (max-width: 768px) {
                .login-card {
                    padding: 30px 25px;
                    margin: 20px;
                }
                
                .brand h1 {
                    font-size: 28px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="login-card">
                <div class="brand">
                    <h1>⚡ BLACKFANG INTELLIGENCE</h1>
                    <p>Advanced Competitive Intelligence Platform</p>
                </div>
                
                <div id="error-message" class="error-message"></div>
                
                <form id="loginForm">
                    <div class="form-group">
                        <label for="email">Email Address</label>
                        <input type="email" id="email" name="email" value="demo@blackfangintel.com" required autocomplete="email">
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" value="demo123" required autocomplete="current-password">
                    </div>
                    
                    <button type="submit" class="login-btn" id="loginBtn">
                        Access Intelligence Platform
                    </button>
                </form>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Authenticating and loading your dashboard...</p>
                </div>
                
                <div class="demo-info">
                    <h3>🎯 Demo Account Access</h3>
                    <p><strong>Email:</strong> demo@blackfangintel.com</p>
                    <p><strong>Password:</strong> demo123</p>
                    <p>Experience the complete competitive intelligence platform with real-time monitoring, threat detection, and strategic recommendations.</p>
                </div>
            </div>
        </div>
        
        <script>
            const API_BASE = '';
            
            function showError(message) {
                const errorDiv = document.getElementById('error-message');
                errorDiv.textContent = message;
                errorDiv.style.display = 'block';
                setTimeout(() => {
                    errorDiv.style.display = 'none';
                }, 5000);
            }
            
            function showLoading(show) {
                const form = document.getElementById('loginForm');
                const loading = document.getElementById('loading');
                const btn = document.getElementById('loginBtn');
                
                if (show) {
                    form.style.display = 'none';
                    loading.style.display = 'block';
                    btn.disabled = true;
                } else {
                    form.style.display = 'block';
                    loading.style.display = 'none';
                    btn.disabled = false;
                }
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
                    const response = await fetch(`${API_BASE}/api/auth/login`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ email, password })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        // Store tokens
                        localStorage.setItem('access_token', data.access_token);
                        localStorage.setItem('refresh_token', data.refresh_token);
                        localStorage.setItem('user_data', JSON.stringify(data.user));
                        
                        // Redirect to dashboard
                        window.location.href = `/dashboard/${data.user.id}`;
                    } else {
                        showError(data.detail || 'Login failed. Please check your credentials.');
                        showLoading(false);
                    }
                } catch (error) {
                    console.error('Login error:', error);
                    showError('Connection error. Please check your internet connection and try again.');
                    showLoading(false);
                }
            });
            
            // Check if already logged in
            if (localStorage.getItem('access_token')) {
                const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
                if (userData.id) {
                    window.location.href = `/dashboard/${userData.id}`;
                }
            }
        </script>
    </body>
    </html>
    """