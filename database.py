"""
BlackFang Intelligence - Database Configuration and Utilities
"""

import asyncio
import logging
from typing import Optional
import asyncpg
from asyncpg import Pool
from config import settings
from auth import AuthManager

# Global database pool
db_pool: Optional[Pool] = None

logger = logging.getLogger(__name__)

async def init_database() -> None:
    """Initialize database connection pool and create tables"""
    global db_pool
    
    if not settings.DATABASE_URL:
        logger.warning("No DATABASE_URL provided - running in demo mode")
        return
    
    try:
        # Create connection pool
        db_pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=settings.DATABASE_POOL_MIN_SIZE,
            max_size=settings.DATABASE_POOL_MAX_SIZE,
            command_timeout=settings.DATABASE_TIMEOUT
        )
        
        logger.info("✅ Database connection pool created")
        
        # Create database schema
        await create_tables()
        
        # Create demo data
        await create_demo_data()
        
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def close_database() -> None:
    """Close database connection pool"""
    global db_pool
    
    if db_pool:
        await db_pool.close()
        db_pool = None
        logger.info("Database connection pool closed")

async def create_tables() -> None:
    """Create database tables if they don't exist"""
    if not db_pool:
        return
    
    async with db_pool.acquire() as conn:
        # Companies table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                company_name VARCHAR(255),
                industry VARCHAR(100),
                subscription_plan VARCHAR(50) DEFAULT 'professional',
                monthly_fee INTEGER DEFAULT 45000,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Competitors table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS competitors (
                id SERIAL PRIMARY KEY,
                company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                website VARCHAR(500) NOT NULL,
                industry VARCHAR(100),
                location VARCHAR(255),
                threat_level VARCHAR(20) DEFAULT 'MEDIUM',
                priority INTEGER DEFAULT 1,
                monitoring_status VARCHAR(20) DEFAULT 'active',
                last_scraped TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(company_id, website)
            )
        """)
        
        # Alerts table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                competitor_id INTEGER REFERENCES competitors(id) ON DELETE CASCADE,
                alert_type VARCHAR(100) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                recommendation TEXT,
                confidence_score DECIMAL(3,2) DEFAULT 0.85,
                is_read BOOLEAN DEFAULT FALSE,
                is_archived BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Scraping data table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS scraping_data (
                id SERIAL PRIMARY KEY,
                competitor_id INTEGER REFERENCES competitors(id) ON DELETE CASCADE,
                data_type VARCHAR(50) NOT NULL,
                raw_data JSONB NOT NULL,
                processed_insights JSONB,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Reports table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id SERIAL PRIMARY KEY,
                company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                report_type VARCHAR(100) NOT NULL,
                content JSONB NOT NULL,
                file_path VARCHAR(500),
                file_size INTEGER,
                download_count INTEGER DEFAULT 0,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User sessions table for refresh tokens
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                refresh_token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # API keys table for external integrations
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                key_name VARCHAR(100) NOT NULL,
                api_key VARCHAR(255) UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                UNIQUE(company_id, key_name)
            )
        """)
        
        # Create indexes for performance
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_competitors_company_id ON competitors(company_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_competitors_threat_level ON competitors(threat_level)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_competitors_monitoring_status ON competitors(monitoring_status)")
        
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_company_id ON alerts(company_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_competitor_id ON alerts(competitor_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_is_read ON alerts(is_read)")
        
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_scraping_data_competitor_id ON scraping_data(competitor_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_scraping_data_scraped_at ON scraping_data(scraped_at DESC)")
        
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_reports_company_id ON reports(company_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_reports_generated_at ON reports(generated_at DESC)")
        
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_company_id ON user_sessions(company_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_refresh_token ON user_sessions(refresh_token)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at)")

async def create_demo_data() -> None:
    """Create comprehensive demo data for client demonstrations"""
    if not db_pool:
        return
    
    async with db_pool.acquire() as conn:
        # Check if demo company already exists
        existing = await conn.fetchrow(
            "SELECT id FROM companies WHERE email = $1", 
            settings.DEMO_EMAIL
        )
        if existing:
            return
        
        auth_manager = AuthManager()
        password_hash = auth_manager.hash_password(settings.DEMO_PASSWORD)
        
        # Create demo company
        company_id = await conn.fetchval("""
            INSERT INTO companies (
                name, email, password_hash, company_name, 
                industry, subscription_plan, monthly_fee
            ) VALUES ($1, $2, $3, $4, $5, $6, $7) 
            RETURNING id
        """, 
            'Demo Automotive Dealership',
            settings.DEMO_EMAIL, 
            password_hash,
            'Demo Motors Pvt Ltd', 
            'Automotive', 
            'professional', 
            45000
        )
        
        # Create demo competitors
        competitors_data = [
            {
                'name': 'AutoMax Dealers',
                'website': 'https://cars24.com',
                'industry': 'Automotive',
                'location': 'Mumbai, Maharashtra',
                'threat_level': 'HIGH',
                'priority': 1
            },
            {
                'name': 'Speed Motors',
                'website': 'https://carwale.com',
                'industry': 'Automotive', 
                'location': 'Delhi, NCR',
                'threat_level': 'MEDIUM',
                'priority': 2
            },
            {
                'name': 'Elite Auto Solutions',
                'website': 'https://cardekho.com',
                'industry': 'Automotive',
                'location': 'Bangalore, Karnataka', 
                'threat_level': 'LOW',
                'priority': 3
            }
        ]
        
        competitor_ids = []
        for comp_data in competitors_data:
            comp_id = await conn.fetchval("""
                INSERT INTO competitors (
                    company_id, name, website, industry, location,
                    threat_level, priority, monitoring_status, last_scraped
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) 
                RETURNING id
            """,
                company_id,
                comp_data['name'],
                comp_data['website'],
                comp_data['industry'],
                comp_data['location'],
                comp_data['threat_level'],
                comp_data['priority'],
                'active',
                asyncio.get_event_loop().time()
            )
            competitor_ids.append(comp_id)
        
        # Create realistic alerts with strategic recommendations
        alerts_data = [
            {
                'competitor_id': competitor_ids[0],
                'alert_type': 'PRICE_DROP',
                'severity': 'HIGH',
                'title': '🔴 CRITICAL: Major Price War Detected - AutoMax Dealers',
                'message': 'AutoMax Dealers implemented aggressive 8% price reduction on Honda City models (₹95,000 decrease). Market share impact imminent within 48 hours. Competitive analysis shows this is part of Q4 market expansion strategy.',
                'recommendation': 'IMMEDIATE ACTION REQUIRED: (1) Consider price matching within 24 hours, OR (2) Launch "Premium Service Value" campaign highlighting superior warranty, service quality, and customer support. (3) Activate loyalty program for existing customers. (4) Prepare inventory management for increased demand.',
                'confidence_score': 0.95
            },
            {
                'competitor_id': competitor_ids[1],
                'alert_type': 'NEW_PROMOTION',
                'severity': 'MEDIUM',
                'title': '🟡 STRATEGIC ALERT: Comprehensive Marketing Campaign - Speed Motors',
                'message': 'Speed Motors launched multi-channel "Monsoon Festival Special" campaign: 5% additional discount + Free comprehensive insurance + Extended warranty + Zero processing fees. Digital ad spend increased 40% across Facebook, Google, and Instagram.',
                'recommendation': 'STRATEGIC RESPONSE WITHIN 72 HOURS: (1) Deploy "Exclusive Client Benefits" package with comparable or superior value proposition. (2) Leverage social media with customer testimonials. (3) Consider partnership with insurance providers for competitive offering. (4) Activate email marketing to warm leads.',
                'confidence_score': 0.87
            },
            {
                'competitor_id': competitor_ids[2],
                'alert_type': 'REPUTATION_ISSUE',
                'severity': 'MEDIUM',
                'title': '🟡 MARKET OPPORTUNITY: Service Quality Issues - Elite Auto',
                'message': 'Elite Auto Solutions received 4 negative reviews (Google: 2, Facebook: 1, Justdial: 1) in past 48 hours citing delivery delays (avg 3 weeks vs promised 1 week), poor after-sales support response times, and parts availability issues. Customer sentiment analysis shows -15% decline.',
                'recommendation': 'COMPETITIVE ADVANTAGE OPPORTUNITY: (1) Launch "Guaranteed Delivery Timeline" campaign with penalty clause for delays. (2) Promote superior after-sales service with same-day response guarantee. (3) Target their dissatisfied customers with "Satisfaction Guarantee" program. (4) Create comparison content highlighting service reliability.',
                'confidence_score': 0.91
            },
            {
                'competitor_id': competitor_ids[0],
                'alert_type': 'CONTENT_CHANGE',
                'severity': 'LOW',
                'title': '🔵 INTELLIGENCE UPDATE: Inventory Strategy Shift - AutoMax',
                'message': 'AutoMax Dealers updated website with 23% increase in premium SUV listings over past 7 days. New featured categories include luxury segment vehicles. Price positioning suggests targeting higher-income demographics.',
                'recommendation': 'STRATEGIC PREPARATION: (1) Review current SUV inventory levels and pricing strategy. (2) Analyze customer data for luxury segment demand in your market. (3) Consider expanding premium vehicle offerings if market data supports. (4) Prepare competitive pricing analysis for luxury segment.',
                'confidence_score': 0.78
            },
            {
                'competitor_id': competitor_ids[1],
                'alert_type': 'TRAFFIC_CHANGE',
                'severity': 'LOW',
                'title': '🔵 MONITORING: Enhanced Digital Presence - Speed Motors',
                'message': 'Speed Motors expanded digital marketing footprint: 40% increase in social media advertising spend, new video marketing campaign launched, website traffic up 25% (estimated). Enhanced SEO efforts detected with new content strategy.',
                'recommendation': 'DIGITAL STRATEGY EVALUATION: (1) Assess current digital marketing budget allocation vs competition. (2) Consider enhanced social media engagement strategy. (3) Evaluate video marketing opportunities for showroom tours, customer testimonials. (4) Review SEO strategy and content calendar.',
                'confidence_score': 0.82
            },
            {
                'competitor_id': competitor_ids[2],
                'alert_type': 'NEW_PRODUCT',
                'severity': 'MEDIUM',
                'title': '🟡 PRODUCT ALERT: Extended Warranty Program - Elite Auto',
                'message': 'Elite Auto Solutions introduced "Total Care Protection" - 5-year extended warranty program with roadside assistance, free annual maintenance, and replacement guarantee. Marketed as premium value addition despite service quality issues.',
                'recommendation': 'SERVICE DIFFERENTIATION OPPORTUNITY: (1) Develop superior warranty program highlighting proven service track record. (2) Create comparison chart showing service quality metrics vs competitors. (3) Bundle extended warranty with proven reliability message. (4) Target customers concerned about long-term service quality.',
                'confidence_score': 0.89
            }
        ]
        
        for alert_data in alerts_data:
            await conn.execute("""
                INSERT INTO alerts (
                    company_id, competitor_id, alert_type, severity, title, 
                    message, recommendation, confidence_score
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                company_id,
                alert_data['competitor_id'],
                alert_data['alert_type'],
                alert_data['severity'],
                alert_data['title'],
                alert_data['message'],
                alert_data['recommendation'],
                alert_data['confidence_score']
            )
        
        # Create sample scraping data
        from datetime import datetime
        import json
        
        scraping_samples = [
            {
                'competitor_id': competitor_ids[0],
                'data_type': 'pricing_analysis',
                'raw_data': {
                    'vehicle_prices': [
                        {
                            'model': 'Honda City', 
                            'current_price': 1105000,
                            'previous_price': 1200000, 
                            'change_percentage': -8.0,
                            'change_amount': -95000
                        },
                        {
                            'model': 'Honda Jazz',
                            'current_price': 875000,
                            'previous_price': 925000,
                            'change_percentage': -5.4,
                            'change_amount': -50000
                        }
                    ],
                    'scraped_timestamp': datetime.utcnow().isoformat(),
                    'scraping_success': True
                },
                'processed_insights': {
                    'trend': 'aggressive_pricing_strategy',
                    'market_impact': 'high',
                    'response_urgency': 'immediate',
                    'competitive_advantage': 'price_leadership',
                    'risk_level': 'high'
                }
            },
            {
                'competitor_id': competitor_ids[1],
                'data_type': 'promotional_analysis',
                'raw_data': {
                    'promotions_detected': [
                        {
                            'title': 'Monsoon Festival Special',
                            'discount_percentage': 5,
                            'additional_benefits': [
                                'Free comprehensive insurance',
                                'Extended warranty',
                                'Zero processing fees'
                            ],
                            'validity': '30 days',
                            'estimated_value': 75000
                        }
                    ],
                    'digital_advertising': {
                        'facebook_ad_spend_increase': '40%',
                        'google_ads_active': True,
                        'instagram_campaign': True
                    },
                    'scraped_timestamp': datetime.utcnow().isoformat()
                },
                'processed_insights': {
                    'campaign_type': 'seasonal_promotion',
                    'market_impact': 'medium',
                    'response_urgency': 'moderate',
                    'investment_level': 'significant',
                    'duration': 'short_term'
                }
            }
        ]
        
        for scraping_data in scraping_samples:
            await conn.execute("""
                INSERT INTO scraping_data (
                    competitor_id, data_type, raw_data, processed_insights
                ) VALUES ($1, $2, $3, $4)
            """,
                scraping_data['competitor_id'],
                scraping_data['data_type'],
                json.dumps(scraping_data['raw_data']),
                json.dumps(scraping_data['processed_insights'])
            )
        
        logger.info("✅ Demo data created with comprehensive automotive scenarios")

# Database utility functions
async def get_company_by_email(email: str):
    """Get company by email"""
    if not db_pool:
        return None
        
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM companies WHERE email = $1 AND is_active = TRUE",
            email
        )

async def get_company_by_id(company_id: int):
    """Get company by ID"""
    if not db_pool:
        return None
        
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM companies WHERE id = $1 AND is_active = TRUE",
            company_id
        )

async def get_competitors_by_company(company_id: int):
    """Get all competitors for a company"""
    if not db_pool:
        return []
        
    async with db_pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM competitors WHERE company_id = $1 ORDER BY priority ASC, threat_level DESC",
            company_id
        )

async def get_alerts_by_company(company_id: int, limit: int = 50, offset: int = 0):
    """Get alerts for a company with pagination"""
    if not db_pool:
        return []
        
    async with db_pool.acquire() as conn:
        return await conn.fetch("""
            SELECT a.*, c.name as competitor_name, c.website as competitor_website
            FROM alerts a
            LEFT JOIN competitors c ON a.competitor_id = c.id
            WHERE a.company_id = $1
            ORDER BY a.created_at DESC
            LIMIT $2 OFFSET $3
        """, company_id, limit, offset)

# Health check function
async def check_database_health() -> dict:
    """Check database connectivity and performance"""
    if not db_pool:
        return {"status": "offline", "error": "No database pool"}
    
    try:
        async with db_pool.acquire() as conn:
            # Test basic connectivity
            result = await conn.fetchval("SELECT 1")
            
            # Test table existence
            tables = await conn.fetch("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            # Get pool statistics
            pool_stats = {
                "size": db_pool.get_size(),
                "idle": db_pool.get_idle_size(),
                "used": db_pool.get_size() - db_pool.get_idle_size()
            }
            
            return {
                "status": "healthy",
                "tables_count": len(tables),
                "pool_stats": pool_stats,
                "connection_test": "passed"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }