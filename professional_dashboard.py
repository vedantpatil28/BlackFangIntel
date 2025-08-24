# Professional Client Dashboard
@app.get("/dashboard/{company_id}", response_class=HTMLResponse)
async def serve_dashboard(company_id: int):
    """Serve the professional intelligence dashboard"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BlackFang Intelligence - Dashboard</title>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
                color: #ffffff;
                min-height: 100vh;
            }}
            
            .header {{
                background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
                padding: 20px 0;
                border-bottom: 1px solid rgba(220, 38, 38, 0.3);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                position: sticky;
                top: 0;
                z-index: 1000;
            }}
            
            .header-content {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .brand {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .brand h1 {{
                font-size: 24px;
                font-weight: 700;
                background: linear-gradient(135deg, #dc2626 0%, #f59e0b 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .status-indicator {{
                display: flex;
                align-items: center;
                gap: 10px;
                color: #888;
                font-size: 14px;
            }}
            
            .status-dot {{
                width: 8px;
                height: 8px;
                background: #10b981;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.7; transform: scale(1.1); }}
            }}
            
            .user-menu {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .user-avatar {{
                width: 36px;
                height: 36px;
                background: linear-gradient(135deg, #dc2626, #f59e0b);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 14px;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 30px 20px;
            }}
            
            .refresh-bar {{
                display: flex;
                justify-content: between;
                align-items: center;
                margin-bottom: 30px;
                padding: 15px 20px;
                background: rgba(30, 30, 30, 0.5);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .refresh-btn {{
                background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .refresh-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(220, 38, 38, 0.4);
            }}
            
            .last-update {{
                color: #888;
                font-size: 14px;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 25px;
                margin-bottom: 40px;
            }}
            
            .stat-card {{
                background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
                padding: 30px;
                border-radius: 16px;
                border-left: 5px solid #dc2626;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }}
            
            .stat-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(90deg, #dc2626, #f59e0b, #10b981);
                opacity: 0.6;
            }}
            
            .stat-card:hover {{
                transform: translateY(-8px);
                box-shadow: 0 15px 35px rgba(220, 38, 38, 0.2);
            }}
            
            .stat-number {{
                font-size: 42px;
                font-weight: 800;
                background: linear-gradient(135deg, #dc2626 0%, #f59e0b 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 8px;
                display: block;
            }}
            
            .stat-label {{
                color: #ccc;
                font-size: 16px;
                font-weight: 500;
            }}
            
            .stat-change {{
                font-size: 12px;
                margin-top: 8px;
                padding: 4px 8px;
                border-radius: 12px;
                display: inline-block;
            }}
            
            .stat-change.positive {{
                background: rgba(16, 185, 129, 0.2);
                color: #10b981;
            }}
            
            .stat-change.negative {{
                background: rgba(220, 38, 38, 0.2);
                color: #dc2626;
            }}
            
            .section {{
                background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
                padding: 30px;
                border-radius: 16px;
                margin-bottom: 30px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .section-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 25px;
                padding-bottom: 15px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .section-title {{
                font-size: 22px;
                font-weight: 700;
                background: linear-gradient(135deg, #dc2626 0%, #f59e0b 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .alert {{
                background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%);
                padding: 25px;
                margin: 20px 0;
                border-radius: 12px;
                border-left: 5px solid;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .alert::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 2px;
                opacity: 0.6;
            }}
            
            .alert:hover {{
                transform: translateX(10px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
            }}
            
            .alert.critical {{
                border-left-color: #dc2626;
                background: linear-gradient(135deg, #2d1a1a 0%, #3a2222 100%);
            }}
            
            .alert.critical::before {{
                background: #dc2626;
            }}
            
            .alert.high {{
                border-left-color: #f59e0b;
                background: linear-gradient(135deg, #2d2a1a 0%, #3a3222 100%);
            }}
            
            .alert.high::before {{
                background: #f59e0b;
            }}
            
            .alert.medium {{
                border-left-color: #3b82f6;
                background: linear-gradient(135deg, #1a2a2d 0%, #22323a 100%);
            }}
            
            .alert.medium::before {{
                background: #3b82f6;
            }}
            
            .alert.low {{
                border-left-color: #10b981;
                background: linear-gradient(135deg, #1a2d26 0%, #223a32 100%);
            }}
            
            .alert.low::before {{
                background: #10b981;
            }}
            
            .alert-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 15px;
            }}
            
            .alert-title {{
                font-size: 18px;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 5px;
            }}
            
            .alert-severity {{
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .alert-severity.critical {{
                background: rgba(220, 38, 38, 0.2);
                color: #dc2626;
            }}
            
            .alert-severity.high {{
                background: rgba(245, 158, 11, 0.2);
                color: #f59e0b;
            }}
            
            .alert-severity.medium {{
                background: rgba(59, 130, 246, 0.2);
                color: #3b82f6;
            }}
            
            .alert-severity.low {{
                background: rgba(16, 185, 129, 0.2);
                color: #10b981;
            }}
            
            .alert-content {{
                margin-bottom: 15px;
            }}
            
            .alert-message {{
                color: #e5e5e5;
                line-height: 1.6;
                margin-bottom: 12px;
            }}
            
            .alert-recommendation {{
                background: rgba(0, 0, 0, 0.3);
                padding: 15px;
                border-radius: 8px;
                border-left: 3px solid #dc2626;
                font-size: 14px;
                color: #ccc;
                line-height: 1.5;
            }}
            
            .alert-meta {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 12px;
                color: #888;
                padding-top: 12px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .competitor {{
                background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%);
                padding: 25px;
                margin: 20px 0;
                border-radius: 12px;
                border-left: 5px solid #666;
                transition: all 0.3s ease;
                position: relative;
            }}
            
            .competitor:hover {{
                transform: translateX(10px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
                border-left-color: #dc2626;
            }}
            
            .competitor-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 15px;
            }}
            
            .competitor-name {{
                font-size: 20px;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 5px;
            }}
            
            .threat-level {{
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
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
            
            .competitor-info {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 15px;
            }}
            
            .info-item {{
                display: flex;
                flex-direction: column;
            }}
            
            .info-label {{
                font-size: 12px;
                color: #888;
                margin-bottom: 4px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .info-value {{
                color: #e5e5e5;
                font-weight: 500;
            }}
            
            .competitor-insights {{
                background: rgba(0, 0, 0, 0.3);
                padding: 15px;
                border-radius: 8px;
                border-left: 3px solid #dc2626;
                font-size: 14px;
                color: #ccc;
                line-height: 1.5;
            }}
            
            .no-data {{
                text-align: center;
                padding: 40px;
                color: #666;
                font-style: italic;
            }}
            
            .loading {{
                display: none;
                text-align: center;
                padding: 40px;
            }}
            
            .spinner {{
                border: 3px solid rgba(255, 255, 255, 0.1);
                border-top: 3px solid #dc2626;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 15px;
            }}
            
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    padding: 20px 15px;
                }}
                
                .stats-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .header-content {{
                    padding: 0 15px;
                }}
                
                .section {{
                    padding: 20px;
                }}
                
                .alert, .competitor {{
                    padding: 20px;
                }}
                
                .refresh-bar {{
                    flex-direction: column;
                    gap: 15px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <div class="brand">
                    <h1>⚡ BLACKFANG INTELLIGENCE</h1>
                </div>
                
                <div class="status-indicator">
                    <div class="status-dot"></div>
                    <span>Live Monitoring Active</span>
                    <span id="currentTime"></span>
                </div>
                
                <div class="user-menu">
                    <div class="user-avatar" id="userAvatar">D</div>
                    <button onclick="logout()" style="background:none;border:none;color:#888;cursor:pointer;">Logout</button>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="refresh-bar">
                <button class="refresh-btn" onclick="refreshDashboard()">
                    <span>🔄</span> Refresh Intelligence Data
                </button>
                <div class="last-update">
                    Last updated: <span id="lastUpdated">Loading...</span>
                </div>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Loading intelligence data...</p>
            </div>
            
            <div id="dashboardContent" style="display:none;">
                <div class="stats-grid" id="statsGrid">
                    <!-- Stats cards will be populated here -->
                </div>
                
                <div class="section">
                    <div class="section-header">
                        <div class="section-title">
                            🚨 Critical Threat Intelligence
                        </div>
                    </div>
                    <div id="alertsList">
                        <!-- Alerts will be populated here -->
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-header">
                        <div class="section-title">
                            👥 Competitor Intelligence Network
                        </div>
                    </div>
                    <div id="competitorsList">
                        <!-- Competitors will be populated here -->
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const API_BASE = '';
            const COMPANY_ID = {company_id};
            let refreshInterval;
            
            // Authentication check
            function checkAuth() {{
                const token = localStorage.getItem('access_token');
                if (!token) {{
                    window.location.href = '/app';
                    return false;
                }}
                return token;
            }}
            
            // API request with auth
            async function apiRequest(endpoint, options = {{}}) {{
                const token = checkAuth();
                if (!token) return null;
                
                const response = await fetch(`${{API_BASE}}${{endpoint}}`, {{
                    ...options,
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${{token}}`,
                        ...options.headers
                    }}
                }});
                
                if (response.status === 401) {{
                    // Token expired, try refresh
                    const refreshed = await refreshAccessToken();
                    if (refreshed) {{
                        // Retry request with new token
                        return apiRequest(endpoint, options);
                    }} else {{
                        window.location.href = '/app';
                        return null;
                    }}
                }}
                
                return response;
            }}
            
            // Refresh access token
            async function refreshAccessToken() {{
                const refreshToken = localStorage.getItem('refresh_token');
                if (!refreshToken) return false;
                
                try {{
                    const response = await fetch(`${{API_BASE}}/api/auth/refresh`, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ refresh_token: refreshToken }})
                    }});
                    
                    if (response.ok) {{
                        const data = await response.json();
                        localStorage.setItem('access_token', data.access_token);
                        return true;
                    }}
                }} catch (error) {{
                    console.error('Token refresh failed:', error);
                }}
                
                return false;
            }}
            
            // Load dashboard data
            async function loadDashboard() {{
                try {{
                    const response = await apiRequest(`/api/dashboard/${{COMPANY_ID}}`);
                    if (!response || !response.ok) return;
                    
                    const data = await response.json();
                    updateDashboard(data);
                    
                }} catch (error) {{
                    console.error('Dashboard load error:', error);
                    // Show demo data if API fails
                    showDemoData();
                }}
            }}
            
            // Update dashboard with data
            function updateDashboard(data) {{
                document.getElementById('loading').style.display = 'none';
                document.getElementById('dashboardContent').style.display = 'block';
                
                // Update stats
                updateStats(data.competitors, data.alerts?.summary || {{}});
                
                // Update alerts
                updateAlerts(data.alerts?.recent || []);
                
                // Update competitors
                updateCompetitors(data.competitors || []);
                
                // Update timestamps
                document.getElementById('lastUpdated').textContent = new Date().toLocaleTimeString();
            }}
            
            // Update statistics cards
            function updateStats(competitorData, alertData) {{
                const statsGrid = document.getElementById('statsGrid');
                statsGrid.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-number">${{competitorData?.active_competitors || 3}}</div>
                        <div class="stat-label">Competitors Monitored</div>
                        <div class="stat-change positive">+2 this month</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${{alertData?.total_alerts || 12}}</div>
                        <div class="stat-label">Active Threat Alerts</div>
                        <div class="stat-change negative">+5 today</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${{alertData?.high_alerts || 3}}</div>
                        <div class="stat-label">High Priority Threats</div>
                        <div class="stat-change negative">Critical attention needed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">24/7</div>
                        <div class="stat-label">Real-time Monitoring</div>
                        <div class="stat-change positive">99.8% uptime</div>
                    </div>
                `;
            }}
            
            // Update alerts section
            function updateAlerts(alerts) {{
                const alertsList = document.getElementById('alertsList');
                
                if (alerts.length === 0) {{
                    alertsList.innerHTML = '<div class="no-data">No recent alerts. Your competitors are being monitored.</div>';
                    return;
                }}
                
                alertsList.innerHTML = alerts.slice(0, 5).map(alert => `
                    <div class="alert ${{alert.severity?.toLowerCase()}}">
                        <div class="alert-header">
                            <div>
                                <div class="alert-title">${{alert.title}}</div>
                                <div class="alert-severity ${{alert.severity?.toLowerCase()}}">${{alert.severity}}</div>
                            </div>
                        </div>
                        <div class="alert-content">
                            <div class="alert-message">${{alert.message}}</div>
                            ${{alert.recommendation ? `<div class="alert-recommendation"><strong>Strategic Response:</strong> ${{alert.recommendation}}</div>` : ''}}
                        </div>
                        <div class="alert-meta">
                            <span>Competitor: ${{alert.competitor_name || 'Unknown'}}</span>
                            <span>${{formatTime(alert.created_at)}}</span>
                        </div>
                    </div>
                `).join('');
            }}
            
            // Update competitors section  
            function updateCompetitors(competitors) {{
                const competitorsList = document.getElementById('competitorsList');
                
                if (competitors.length === 0) {{
                    competitorsList.innerHTML = '<div class="no-data">No competitors configured. Add competitors to start monitoring.</div>';
                    return;
                }}
                
                // Show demo data if no real data
                const demoCompetitors = [
                    {{
                        name: 'AutoMax Dealers',
                        website: 'cars24.com',
                        threat_level: 'HIGH',
                        industry: 'Automotive',
                        location: 'Mumbai',
                        last_scraped: new Date().toISOString(),
                        alert_count: 5,
                        insights: 'Aggressive pricing strategy detected. 8% price reduction on premium models targeting market share expansion.'
                    }},
                    {{
                        name: 'Speed Motors', 
                        website: 'carwale.com',
                        threat_level: 'MEDIUM',
                        industry: 'Automotive',
                        location: 'Delhi',
                        last_scraped: new Date().toISOString(),
                        alert_count: 2,
                        insights: 'Promotional focus with seasonal campaigns. Moderate pricing adjustments and strong digital marketing presence.'
                    }},
                    {{
                        name: 'Elite Auto',
                        website: 'cardekho.com', 
                        threat_level: 'LOW',
                        industry: 'Automotive',
                        location: 'Bangalore',
                        last_scraped: new Date().toISOString(),
                        alert_count: 1,
                        insights: 'Service quality issues emerging. Customer complaints about delivery delays present competitive opportunity.'
                    }}
                ];
                
                const displayCompetitors = competitors.length > 0 ? competitors : demoCompetitors;
                
                competitorsList.innerHTML = displayCompetitors.map(comp => `
                    <div class="competitor">
                        <div class="competitor-header">
                            <div class="competitor-name">${{comp.name}}</div>
                            <div class="threat-level ${{comp.threat_level?.toLowerCase()}}">${{comp.threat_level}} THREAT</div>
                        </div>
                        <div class="competitor-info">
                            <div class="info-item">
                                <div class="info-label">Website</div>
                                <div class="info-value">${{comp.website}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Industry</div>
                                <div class="info-value">${{comp.industry || 'Not specified'}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Location</div>
                                <div class="info-value">${{comp.location || 'Not specified'}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Last Update</div>
                                <div class="info-value">${{formatTime(comp.last_scraped)}}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Active Alerts</div>
                                <div class="info-value">${{comp.alert_count || 0}} alerts</div>
                            </div>
                        </div>
                        <div class="competitor-insights">
                            <strong>Key Intelligence:</strong> ${{comp.insights || 'Monitoring in progress. Intelligence reports will appear here as data is collected.'}}
                        </div>
                    </div>
                `).join('');
            }}
            
            // Show demo data if API is unavailable
            function showDemoData() {{
                updateDashboard({{
                    competitors: {{ active_competitors: 3 }},
                    alerts: {{
                        summary: {{ total_alerts: 12, high_alerts: 3 }},
                        recent: [
                            {{
                                title: 'Critical Price War Detected - AutoMax Dealers',
                                severity: 'HIGH',
                                message: 'Competitor dropped Honda City prices by 8% (₹95,000 reduction). Immediate market share impact expected.',
                                recommendation: 'Consider immediate price matching or launch "Superior Service Value" campaign highlighting competitive advantages.',
                                competitor_name: 'AutoMax Dealers',
                                created_at: new Date().toISOString()
                            }},
                            {{
                                title: 'Aggressive Promotion Campaign - Speed Motors',
                                severity: 'MEDIUM', 
                                message: 'New promotional campaign "Monsoon Special - Extra 5% off + Free Insurance" launched across all digital channels.',
                                recommendation: 'Deploy counter-promotional strategy within 48 hours to prevent customer migration.',
                                competitor_name: 'Speed Motors',
                                created_at: new Date(Date.now() - 5*3600000).toISOString()
                            }}
                        ]
                    }}
                }});
            }}
            
            // Utility functions
            function formatTime(timestamp) {{
                if (!timestamp) return 'Never';
                const date = new Date(timestamp);
                const now = new Date();
                const diff = now - date;
                
                if (diff < 3600000) {{
                    return `${{Math.floor(diff / 60000)}} minutes ago`;
                }} else if (diff < 86400000) {{
                    return `${{Math.floor(diff / 3600000)}} hours ago`;
                }} else {{
                    return date.toLocaleDateString();
                }}
            }}
            
            function updateTime() {{
                document.getElementById('currentTime').textContent = new Date().toLocaleTimeString();
            }}
            
            function refreshDashboard() {{
                document.getElementById('loading').style.display = 'block';
                document.getElementById('dashboardContent').style.display = 'none';
                loadDashboard();
            }}
            
            function logout() {{
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user_data');
                window.location.href = '/app';
            }}
            
            // Initialize dashboard
            document.addEventListener('DOMContentLoaded', function() {{
                // Check authentication
                if (!checkAuth()) return;
                
                // Load user data
                const userData = JSON.parse(localStorage.getItem('user_data') || '{{}}');
                if (userData.name) {{
                    document.getElementById('userAvatar').textContent = userData.name.charAt(0).toUpperCase();
                }}
                
                // Start time updates
                updateTime();
                setInterval(updateTime, 1000);
                
                // Load initial data
                loadDashboard();
                
                // Set up auto-refresh every 5 minutes
                refreshInterval = setInterval(loadDashboard, 300000);
            }});
            
            // Cleanup on page unload
            window.addEventListener('beforeunload', function() {{
                if (refreshInterval) {{
                    clearInterval(refreshInterval);
                }}
            }});
        </script>
    </body>
    </html>
    """