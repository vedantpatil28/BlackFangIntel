#!/usr/bin/env python3
"""
BLACKFANG INTELLIGENCE - PRODUCTION APPLICATION
Complete competitive intelligence platform for SMBs
Author: AI Development Team
Version: 2.0.0 Production
"""

import os
import asyncio
import logging
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import re
from decimal import Decimal

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

# Database and async imports
import asyncpg
from asyncpg import Pool
import aiohttp
import aiofiles
import aioredis
from celery import Celery

# Data processing imports  
from bs4 import BeautifulSoup
import pandas as pd
from textblob import TextBlob
import requests
from urllib.parse import urlparse, urljoin
import time
import random

# Email and notification imports
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# PDF and reporting imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('blackfang.log')
    ]
)
logger = logging.getLogger(__name__)

# Environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:blackfang2025@localhost:5432/blackfang_prod')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
JWT_SECRET = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY', '')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# Global variables
db_pool: Optional[Pool] = None
redis_client = None
celery_app = None

# Initialize Celery for background tasks
celery_app = Celery(
    'blackfang_tasks',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['tasks.scraping', 'tasks.alerts', 'tasks.reports']
)

# Database Models and Schema
class DatabaseManager:
    def __init__(self, pool: Pool):
        self.pool = pool
    
    async def initialize_schema(self):
        """Initialize all database tables"""
        async with self.pool.acquire() as conn:
            # Companies table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    company_name VARCHAR(255),
                    industry VARCHAR(100),
                    phone VARCHAR(50),
                    website VARCHAR(500),
                    address TEXT,
                    subscription_plan VARCHAR(50) DEFAULT 'basic',
                    subscription_status VARCHAR(50) DEFAULT 'active',
                    monthly_fee INTEGER DEFAULT 25000,
                    billing_cycle VARCHAR(20) DEFAULT 'monthly',
                    trial_ends_at TIMESTAMP,
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
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
                    google_place_id VARCHAR(255),
                    facebook_page_id VARCHAR(255),
                    linkedin_company_id VARCHAR(255),
                    monitoring_status VARCHAR(50) DEFAULT 'active',
                    monitoring_frequency INTEGER DEFAULT 360, -- minutes
                    threat_level VARCHAR(20) DEFAULT 'MEDIUM',
                    priority INTEGER DEFAULT 1,
                    last_scraped_at TIMESTAMP,
                    scraping_errors INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, website)
                )
            """)
            
            # Scraping data table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS competitor_data (
                    id SERIAL PRIMARY KEY,
                    competitor_id INTEGER REFERENCES competitors(id) ON DELETE CASCADE,
                    data_type VARCHAR(50) NOT NULL, -- 'website', 'reviews', 'social', 'pricing'
                    raw_data JSONB NOT NULL,
                    processed_data JSONB,
                    metadata JSONB,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processing_status VARCHAR(50) DEFAULT 'pending',
                    error_message TEXT
                )
            """)
            
            # Alerts table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                    competitor_id INTEGER REFERENCES competitors(id) ON DELETE CASCADE,
                    alert_type VARCHAR(100) NOT NULL,
                    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
                    title VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    recommendation TEXT,
                    data_snapshot JSONB,
                    is_read BOOLEAN DEFAULT FALSE,
                    is_dismissed BOOLEAN DEFAULT FALSE,
                    notification_sent BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """)
            
            # Reports table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                    title VARCHAR(255) NOT NULL,
                    report_type VARCHAR(50) NOT NULL, -- 'weekly', 'monthly', 'custom'
                    content JSONB NOT NULL,
                    file_path VARCHAR(500),
                    file_size INTEGER,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    email_sent BOOLEAN DEFAULT FALSE,
                    download_count INTEGER DEFAULT 0
                )
            """)
            
            # Settings table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS company_settings (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                    setting_key VARCHAR(100) NOT NULL,
                    setting_value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, setting_key)
                )
            """)
            
            # API keys table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                    key_name VARCHAR(100) NOT NULL,
                    api_key VARCHAR(255) UNIQUE NOT NULL,
                    permissions TEXT[] DEFAULT '{}',
                    last_used_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Audit log table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER REFERENCES companies(id) ON DELETE SET NULL,
                    action VARCHAR(100) NOT NULL,
                    resource_type VARCHAR(50),
                    resource_id INTEGER,
                    old_values JSONB,
                    new_values JSONB,
                    ip_address INET,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_competitors_company_id ON competitors(company_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_competitor_data_competitor_id ON competitor_data(competitor_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_competitor_data_scraped_at ON competitor_data(scraped_at DESC)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_company_id ON alerts(company_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_reports_company_id ON reports(company_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_company_id ON audit_logs(company_id)")
            
        logger.info("✅ Database schema initialized successfully")

# Authentication and Security
class AuthManager:
    def __init__(self):
        self.secret_key = JWT_SECRET
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 30
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt-like approach"""
        salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() + ':' + salt
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            stored_hash, salt = hashed.split(':')
            return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() == stored_hash
        except:
            return False
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: dict):
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

# Competitive Intelligence Scraper
class IntelligenceScraper:
    def __init__(self):
        self.session_timeout = 30
        self.max_retries = 3
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
    
    async def scrape_competitor_website(self, competitor: dict) -> dict:
        """Scrape comprehensive competitor website data"""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.session_timeout),
                headers={'User-Agent': random.choice(self.user_agents)}
            ) as session:
                
                # Main website content
                website_data = await self._scrape_website_content(session, competitor['website'])
                
                # Pricing information
                pricing_data = await self._extract_pricing_data(website_data['html'])
                
                # Promotional content
                promotions = await self._extract_promotional_content(website_data['html'])
                
                # Contact information
                contact_info = await self._extract_contact_information(website_data['html'])
                
                # Meta information
                meta_data = await self._extract_meta_information(website_data['html'])
                
                # Social media links
                social_links = await self._extract_social_media_links(website_data['html'])
                
                return {
                    'competitor_id': competitor['id'],
                    'scraped_at': datetime.utcnow().isoformat(),
                    'website_data': website_data,
                    'pricing_data': pricing_data,
                    'promotions': promotions,
                    'contact_info': contact_info,
                    'meta_data': meta_data,
                    'social_links': social_links,
                    'scraping_success': True,
                    'error_count': 0
                }
                
        except Exception as e:
            logger.error(f"Scraping failed for {competitor['website']}: {str(e)}")
            return {
                'competitor_id': competitor['id'],
                'scraped_at': datetime.utcnow().isoformat(),
                'scraping_success': False,
                'error_message': str(e),
                'error_count': 1
            }
    
    async def _scrape_website_content(self, session: aiohttp.ClientSession, url: str) -> dict:
        """Scrape basic website content"""
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    return {
                        'url': url,
                        'status_code': response.status,
                        'html': html,
                        'title': soup.title.string if soup.title else '',
                        'meta_description': self._get_meta_description(soup),
                        'headings': self._extract_headings(soup),
                        'content_text': soup.get_text(),
                        'links_count': len(soup.find_all('a')),
                        'images_count': len(soup.find_all('img')),
                        'page_size': len(html)
                    }
                else:
                    return {'error': f'HTTP {response.status}', 'url': url}
                    
        except Exception as e:
            return {'error': str(e), 'url': url}
    
    def _extract_pricing_data(self, html: str) -> List[dict]:
        """Extract pricing information from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        pricing_patterns = [
            r'₹\s*[\d,]+(?:\.\d{2})?',
            r'Rs\.?\s*[\d,]+(?:\.\d{2})?',
            r'\$\s*[\d,]+(?:\.\d{2})?',
            r'Price[:\s]*₹?\s*[\d,]+',
            r'Cost[:\s]*₹?\s*[\d,]+'
        ]
        
        prices = []
        text = soup.get_text()
        
        for pattern in pricing_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:20]:  # Limit to prevent spam
                clean_price = re.sub(r'[^\d,.]', '', match)
                if clean_price and len(clean_price) > 2:
                    prices.append({
                        'raw_text': match.strip(),
                        'cleaned_price': clean_price,
                        'estimated_value': self._extract_numeric_value(clean_price),
                        'context': self._get_price_context(soup, match),
                        'confidence': 0.8
                    })
        
        return prices[:10]  # Return top 10 prices
    
    def _extract_promotional_content(self, html: str) -> List[dict]:
        """Extract promotional offers and campaigns"""
        soup = BeautifulSoup(html, 'html.parser')
        promo_keywords = [
            'sale', 'discount', 'offer', 'deal', 'special', 'limited',
            'off', 'free', 'bonus', 'save', 'reduced', 'clearance',
            'promotion', 'combo', 'package', 'bundle', 'cashback'
        ]
        
        promotions = []
        
        # Check for promotional elements
        promo_elements = soup.find_all(['div', 'span', 'p', 'h1', 'h2', 'h3'], 
                                      class_=re.compile(r'promo|sale|offer|deal|discount', re.I))
        
        for element in promo_elements[:10]:
            text = element.get_text(strip=True)
            if 10 <= len(text) <= 200:
                promotions.append({
                    'text': text,
                    'element_type': element.name,
                    'source': 'html_element',
                    'confidence': 0.9
                })
        
        # Check text for promotional keywords
        text_content = soup.get_text().lower()
        sentences = re.split(r'[.!?]', text_content)
        
        for sentence in sentences:
            for keyword in promo_keywords:
                if keyword in sentence and 20 <= len(sentence.strip()) <= 150:
                    promotions.append({
                        'text': sentence.strip(),
                        'keyword': keyword,
                        'source': 'text_analysis',
                        'confidence': 0.7
                    })
                    if len(promotions) >= 15:
                        break
            if len(promotions) >= 15:
                break
        
        return promotions[:10]
    
    def _extract_contact_information(self, html: str) -> dict:
        """Extract contact information"""
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        # Phone numbers
        phone_patterns = [
            r'\+91[\s-]?\d{10}',
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}'
        ]
        
        # Email addresses
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # Address patterns
        address_keywords = ['address', 'location', 'office', 'store', 'branch']
        
        phones = []
        emails = []
        addresses = []
        
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        emails = re.findall(email_pattern, text)
        
        # Simple address extraction
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in address_keywords) and len(line) > 20:
                addresses.append(line[:200])
        
        return {
            'phones': list(set(phones))[:5],
            'emails': list(set(emails))[:5],
            'addresses': addresses[:3]
        }
    
    def _extract_meta_information(self, html: str) -> dict:
        """Extract meta information from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        return {
            'title': soup.title.string if soup.title else '',
            'meta_description': self._get_meta_description(soup),
            'meta_keywords': self._get_meta_keywords(soup),
            'canonical_url': self._get_canonical_url(soup),
            'og_title': self._get_og_tag(soup, 'og:title'),
            'og_description': self._get_og_tag(soup, 'og:description'),
            'og_image': self._get_og_tag(soup, 'og:image')
        }
    
    def _extract_social_media_links(self, html: str) -> dict:
        """Extract social media profile links"""
        soup = BeautifulSoup(html, 'html.parser')
        social_platforms = {
            'facebook': r'facebook\.com/[\w.-]+',
            'twitter': r'twitter\.com/[\w.-]+',
            'linkedin': r'linkedin\.com/[\w.-/]+',
            'instagram': r'instagram\.com/[\w.-]+',
            'youtube': r'youtube\.com/[\w.-/]+'
        }
        
        links = {}
        all_links = soup.find_all('a', href=True)
        
        for platform, pattern in social_platforms.items():
            for link in all_links:
                href = link['href']
                if re.search(pattern, href, re.IGNORECASE):
                    links[platform] = href
                    break
        
        return links
    
    # Helper methods
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        meta = soup.find('meta', attrs={'name': 'description'})
        return meta.get('content', '') if meta else ''
    
    def _get_meta_keywords(self, soup: BeautifulSoup) -> str:
        meta = soup.find('meta', attrs={'name': 'keywords'})
        return meta.get('content', '') if meta else ''
    
    def _get_canonical_url(self, soup: BeautifulSoup) -> str:
        link = soup.find('link', attrs={'rel': 'canonical'})
        return link.get('href', '') if link else ''
    
    def _get_og_tag(self, soup: BeautifulSoup, property_name: str) -> str:
        meta = soup.find('meta', attrs={'property': property_name})
        return meta.get('content', '') if meta else ''
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[dict]:
        """Extract all headings from HTML"""
        headings = []
        for level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for heading in soup.find_all(level):
                text = heading.get_text(strip=True)
                if text and len(text) <= 200:
                    headings.append({
                        'level': level,
                        'text': text
                    })
        return headings[:20]
    
    def _extract_numeric_value(self, price_str: str) -> float:
        """Extract numeric value from price string"""
        try:
            # Remove commas and convert to float
            clean_str = price_str.replace(',', '')
            return float(clean_str)
        except:
            return 0.0
    
    def _get_price_context(self, soup: BeautifulSoup, price_text: str) -> str:
        """Get context around price mention"""
        text = soup.get_text()
        index = text.find(price_text)
        if index > -1:
            start = max(0, index - 50)
            end = min(len(text), index + len(price_text) + 50)
            return text[start:end].strip()
        return ''

# Application Lifespan Management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global db_pool, redis_client
    
    logger.info("🚀 Starting BlackFang Intelligence Production System...")
    
    try:
        # Initialize database connection pool
        db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=5,
            max_size=20,
            command_timeout=60,
            server_settings={
                'jit': 'off'
            }
        )
        logger.info("✅ Database connection pool created")
        
        # Initialize database schema
        db_manager = DatabaseManager(db_pool)
        await db_manager.initialize_schema()
        
        # Initialize Redis connection
        redis_client = await aioredis.from_url(REDIS_URL)
        logger.info("✅ Redis connection established")
        
        # Initialize demo data
        await create_demo_data()
        logger.info("✅ Demo data initialized")
        
        logger.info("🎯 BlackFang Intelligence is OPERATIONAL")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Cleanup
    if db_pool:
        await db_pool.close()
        logger.info("🗄️ Database pool closed")
    
    if redis_client:
        await redis_client.close()
        logger.info("📦 Redis connection closed")
    
    logger.info("🛑 BlackFang Intelligence shut down gracefully")

# Initialize FastAPI Application
app = FastAPI(
    title="BlackFang Intelligence",
    description="Advanced Competitive Intelligence Platform for SMBs",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Middleware Configuration
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if ENVIRONMENT == "development" else ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

if ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=ALLOWED_HOSTS
    )

# Initialize managers
auth_manager = AuthManager()
scraper = IntelligenceScraper()
security = HTTPBearer()

async def create_demo_data():
    """Create comprehensive demo data for testing"""
    if not db_pool:
        return
    
    async with db_pool.acquire() as conn:
        # Check if demo company exists
        existing = await conn.fetchrow(
            "SELECT id FROM companies WHERE email = 'demo@blackfangintel.com'"
        )
        if existing:
            return
        
        # Create demo company
        password_hash = auth_manager.hash_password('demo123')
        company_id = await conn.fetchval("""
            INSERT INTO companies (
                name, email, password_hash, company_name, industry, 
                subscription_plan, monthly_fee, phone, website, address
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) 
            RETURNING id
        """, 
            'Demo Automotive Dealership',
            'demo@blackfangintel.com', 
            password_hash,
            'Demo Motors Pvt Ltd',
            'Automotive',
            'professional',
            45000,
            '+91 98765 43210',
            'https://demomotors.com',
            '123 Business Park, Mumbai, Maharashtra'
        )
        
        # Create demo competitors
        competitors = [
            {
                'name': 'AutoMax Dealers',
                'website': 'https://cars24.com',
                'industry': 'Automotive',
                'location': 'Mumbai',
                'threat_level': 'HIGH',
                'priority': 1
            },
            {
                'name': 'Speed Motors',
                'website': 'https://carwale.com',
                'industry': 'Automotive', 
                'location': 'Delhi',
                'threat_level': 'MEDIUM',
                'priority': 2
            },
            {
                'name': 'Elite Auto',
                'website': 'https://cardekho.com',
                'industry': 'Automotive',
                'location': 'Bangalore',
                'threat_level': 'LOW',
                'priority': 3
            }
        ]
        
        competitor_ids = []
        for comp in competitors:
            comp_id = await conn.fetchval("""
                INSERT INTO competitors (
                    company_id, name, website, industry, location, 
                    threat_level, priority, monitoring_status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """, 
                company_id, comp['name'], comp['website'], 
                comp['industry'], comp['location'], comp['threat_level'], 
                comp['priority'], 'active'
            )
            competitor_ids.append(comp_id)
        
        # Create demo alerts
        demo_alerts = [
            {
                'competitor_id': competitor_ids[0],
                'alert_type': 'PRICE_DROP',
                'severity': 'HIGH',
                'title': 'Critical Price War Detected',
                'message': 'AutoMax Dealers dropped Honda City prices by 8% (₹95,000 reduction). Immediate market share impact expected.',
                'recommendation': 'Consider immediate price matching or launch "Superior Service Value" campaign highlighting competitive advantages.',
                'data_snapshot': json.dumps({
                    'previous_price': 1200000,
                    'new_price': 1105000,
                    'change_percentage': -8.0,
                    'models_affected': ['Honda City', 'Honda Jazz'],
                    'effective_date': datetime.utcnow().isoformat()
                })
            },
            {
                'competitor_id': competitor_ids[1],
                'alert_type': 'NEW_PROMOTION',
                'severity': 'MEDIUM',
                'title': 'Aggressive Promotion Campaign',
                'message': 'Speed Motors launched "Monsoon Special - Extra 5% off + Free Insurance" across all digital channels.',
                'recommendation': 'Deploy counter-promotional strategy within 48 hours to prevent customer migration.',
                'data_snapshot': json.dumps({
                    'promotion_name': 'Monsoon Special',
                    'discount_percentage': 5,
                    'additional_benefits': ['Free Insurance', 'Extended Warranty'],
                    'campaign_duration': '30 days',
                    'channels': ['Website', 'Social Media', 'Email']
                })
            },
            {
                'competitor_id': competitor_ids[2],
                'alert_type': 'REPUTATION_ISSUE',
                'severity': 'MEDIUM',
                'title': 'Service Quality Concerns',
                'message': '3 negative reviews about delivery delays posted in past 24 hours. Customer sentiment declining.',
                'recommendation': 'Target "Fast & Reliable Service" messaging in marketing campaigns to capitalize on competitor weakness.',
                'data_snapshot': json.dumps({
                    'negative_reviews_count': 3,
                    'common_complaints': ['Delivery Delays', 'Poor Communication', 'Service Quality'],
                    'sentiment_score': -0.6,
                    'review_sources': ['Google Reviews', 'Facebook', 'Just Dial']
                })
            }
        ]
        
        for alert in demo_alerts:
            await conn.execute("""
                INSERT INTO alerts (
                    company_id, competitor_id, alert_type, severity, 
                    title, message, recommendation, data_snapshot
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                company_id, alert['competitor_id'], alert['alert_type'],
                alert['severity'], alert['title'], alert['message'],
                alert['recommendation'], alert['data_snapshot']
            )
        
        # Create demo settings
        default_settings = [
            ('email_notifications', 'true'),
            ('alert_frequency', 'immediate'),
            ('report_frequency', 'weekly'),
            ('monitoring_hours', '24x7'),
            ('alert_threshold_high', '5'),
            ('alert_threshold_medium', '10'),
            ('dashboard_refresh_rate', '30')
        ]
        
        for setting_key, setting_value in default_settings:
            await conn.execute("""
                INSERT INTO company_settings (company_id, setting_key, setting_value)
                VALUES ($1, $2, $3)
                ON CONFLICT (company_id, setting_key) DO NOTHING
            """, company_id, setting_key, setting_value)
        
        logger.info("✅ Demo data created successfully")

# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user"""
    try:
        payload = auth_manager.decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        company_id = payload.get("company_id")
        if not company_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # Get user from database
        async with db_pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM companies WHERE id = $1 AND is_active = TRUE",
                company_id
            )
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            return dict(user)
    
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# API Routes
@app.get("/", response_model=dict)
async def root():
    """API root endpoint"""
    return {
        "message": "🎯 BlackFang Intelligence API v2.0",
        "status": "operational",
        "version": "2.0.0",
        "environment": ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "authentication": "/api/auth",
            "dashboard": "/app",
            "api_docs": "/api/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": ENVIRONMENT
    }
    
    # Check database
    try:
        if db_pool:
            async with db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            health_status["database"] = "connected"
        else:
            health_status["database"] = "disconnected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        if redis_client:
            await redis_client.ping()
            health_status["redis"] = "connected"
        else:
            health_status["redis"] = "disconnected"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
    
    # System metrics
    import psutil
    health_status["system"] = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }
    
    return health_status

# Authentication endpoints
@app.post("/api/auth/login")
async def login(request: Request):
    """User login endpoint"""
    try:
        data = await request.json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        
        # Get user from database
        async with db_pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM companies WHERE email = $1 AND is_active = TRUE",
                email
            )
            
            if not user or not auth_manager.verify_password(password, user['password_hash']):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Update last login
            await conn.execute(
                "UPDATE companies SET last_login = CURRENT_TIMESTAMP WHERE id = $1",
                user['id']
            )
            
            # Create tokens
            token_data = {"company_id": user['id'], "email": user['email']}
            access_token = auth_manager.create_access_token(token_data)
            refresh_token = auth_manager.create_refresh_token(token_data)
            
            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": auth_manager.access_token_expire_minutes * 60,
                "user": {
                    "id": user['id'],
                    "name": user['name'],
                    "email": user['email'],
                    "company_name": user['company_name'],
                    "subscription_plan": user['subscription_plan'],
                    "subscription_status": user['subscription_status']
                }
            }
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/api/auth/refresh")
async def refresh_token(request: Request):
    """Refresh access token"""
    try:
        data = await request.json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token required")
        
        # Decode refresh token
        payload = auth_manager.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        # Create new access token
        token_data = {"company_id": payload['company_id'], "email": payload['email']}
        new_access_token = auth_manager.create_access_token(token_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": auth_manager.access_token_expire_minutes * 60
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=401, detail="Token refresh failed")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
        reload=ENVIRONMENT == "development"
    )