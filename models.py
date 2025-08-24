"""
BlackFang Intelligence - Database Models and Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from enum import Enum

# Enums for database choices
class SubscriptionPlan(str, Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class ThreatLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class MonitoringStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    INACTIVE = "inactive"

class AlertType(str, Enum):
    PRICE_DROP = "PRICE_DROP"
    PRICE_INCREASE = "PRICE_INCREASE"
    NEW_PROMOTION = "NEW_PROMOTION"
    CONTENT_CHANGE = "CONTENT_CHANGE"
    NEW_PRODUCT = "NEW_PRODUCT"
    REPUTATION_ISSUE = "REPUTATION_ISSUE"
    TRAFFIC_CHANGE = "TRAFFIC_CHANGE"
    RANKING_CHANGE = "RANKING_CHANGE"

# Pydantic models for API requests/responses
class CompanyBase(BaseModel):
    name: str
    email: EmailStr
    company_name: Optional[str] = None
    industry: Optional[str] = None
    subscription_plan: SubscriptionPlan = SubscriptionPlan.PROFESSIONAL

class CompanyCreate(CompanyBase):
    password: str

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    subscription_plan: Optional[SubscriptionPlan] = None

class CompanyResponse(CompanyBase):
    id: int
    is_active: bool
    created_at: datetime
    monthly_fee: int
    
    class Config:
        from_attributes = True

class CompetitorBase(BaseModel):
    name: str
    website: str
    industry: Optional[str] = None
    location: Optional[str] = None
    threat_level: ThreatLevel = ThreatLevel.MEDIUM
    priority: int = 1

    @validator('website')
    def validate_website(cls, v):
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        return v

class CompetitorCreate(CompetitorBase):
    company_id: int

class CompetitorUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    threat_level: Optional[ThreatLevel] = None
    priority: Optional[int] = None
    monitoring_status: Optional[MonitoringStatus] = None

class CompetitorResponse(CompetitorBase):
    id: int
    company_id: int
    monitoring_status: MonitoringStatus
    last_scraped: Optional[datetime] = None
    created_at: datetime
    
    # Additional computed fields
    alert_count: Optional[int] = 0
    last_alert_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    recommendation: Optional[str] = None
    confidence_score: float = 0.85

    @validator('confidence_score')
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Confidence score must be between 0 and 1')
        return v

class AlertCreate(AlertBase):
    company_id: int
    competitor_id: int

class AlertUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None

class AlertResponse(AlertBase):
    id: int
    company_id: int
    competitor_id: int
    is_read: bool = False
    is_archived: bool = False
    created_at: datetime
    
    # Related data
    competitor_name: Optional[str] = None
    competitor_website: Optional[str] = None
    
    class Config:
        from_attributes = True

class ScrapingDataBase(BaseModel):
    data_type: str
    raw_data: dict
    processed_insights: Optional[dict] = None

class ScrapingDataCreate(ScrapingDataBase):
    competitor_id: int

class ScrapingDataResponse(ScrapingDataBase):
    id: int
    competitor_id: int
    scraped_at: datetime
    
    class Config:
        from_attributes = True

class ReportBase(BaseModel):
    title: str
    report_type: str
    content: dict
    file_path: Optional[str] = None

class ReportCreate(ReportBase):
    company_id: int

class ReportResponse(ReportBase):
    id: int
    company_id: int
    generated_at: datetime
    file_size: Optional[int] = None
    download_count: int = 0
    
    class Config:
        from_attributes = True

# Authentication models
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    company_id: Optional[int] = None
    email: Optional[str] = None
    subscription_plan: Optional[str] = None

class RefreshToken(BaseModel):
    refresh_token: str

# Dashboard models
class DashboardStats(BaseModel):
    total_competitors: int
    active_competitors: int
    total_alerts: int
    unread_alerts: int
    high_priority_alerts: int
    today_alerts: int
    week_alerts: int

class CompetitorStats(BaseModel):
    high_threat_count: int
    medium_threat_count: int
    low_threat_count: int
    active_monitoring_count: int

class DashboardData(BaseModel):
    company: CompanyResponse
    statistics: DashboardStats
    competitor_stats: CompetitorStats
    recent_alerts: List[AlertResponse]
    top_competitors: List[CompetitorResponse]
    system_status: dict

# Intelligence analysis models
class PriceData(BaseModel):
    raw_text: str
    cleaned_value: str
    currency: Optional[str] = "INR"
    context: Optional[str] = None

class PromotionData(BaseModel):
    text: str
    keyword_trigger: str
    confidence_score: float
    context: Optional[str] = None

class ContentAnalysis(BaseModel):
    total_text_length: int
    heading_count: int
    image_count: int
    link_count: int
    has_contact_form: bool
    has_pricing_section: bool
    language: Optional[str] = "en"

class ScrapingResult(BaseModel):
    url: str
    success: bool
    title: Optional[str] = None
    prices: List[PriceData] = []
    promotions: List[PromotionData] = []
    content_analysis: Optional[ContentAnalysis] = None
    scraped_at: datetime
    error: Optional[str] = None

# Notification models
class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: str
    priority: str = "MEDIUM"

class EmailNotification(NotificationBase):
    recipient_email: EmailStr
    template_name: Optional[str] = None
    template_data: Optional[dict] = None

class SMSNotification(NotificationBase):
    recipient_phone: str
    
# Business intelligence models
class CompetitorInsight(BaseModel):
    competitor_id: int
    competitor_name: str
    threat_level: ThreatLevel
    key_findings: List[str]
    recommendations: List[str]
    confidence_score: float
    last_updated: datetime

class MarketAnalysis(BaseModel):
    industry: str
    total_competitors: int
    market_trends: List[str]
    opportunities: List[str]
    threats: List[str]
    generated_at: datetime

class IntelligenceReport(BaseModel):
    company_id: int
    report_period: str
    competitor_insights: List[CompetitorInsight]
    market_analysis: MarketAnalysis
    executive_summary: str
    action_items: List[str]
    generated_at: datetime

# API Response models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

# WebSocket models for real-time updates
class WebSocketMessage(BaseModel):
    type: str
    data: dict
    timestamp: datetime = datetime.utcnow()

class AlertUpdate(WebSocketMessage):
    alert_id: int
    company_id: int
    
class ScrapingUpdate(WebSocketMessage):
    competitor_id: int
    company_id: int
    status: str