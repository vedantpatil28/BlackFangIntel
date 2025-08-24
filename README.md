# BlackFang Intelligence - Complete Competitive Intelligence Platform

## 🎯 Project Overview

BlackFang Intelligence is a professional competitive intelligence platform designed for SMBs (Small to Medium Businesses). It provides real-time competitor monitoring, threat detection, and strategic recommendations.

## 🏗️ Architecture

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with async connections
- **Frontend**: Modern HTML5/CSS3/JavaScript
- **Authentication**: JWT token-based security
- **Deployment**: Railway.app with Docker support

## 📋 Features

### Core Intelligence Features
- **Real-time Competitor Monitoring**: 24/7 automated website scraping
- **Threat Detection**: AI-powered analysis of competitive moves
- **Strategic Recommendations**: Actionable business intelligence
- **Alert System**: Instant notifications for critical changes
- **Professional Dashboard**: Real-time intelligence interface

### Business Features
- **Multi-client Support**: Scalable SaaS architecture
- **Subscription Management**: Tiered pricing plans
- **Professional Authentication**: Secure JWT-based login
- **Mobile Responsive**: Works on all devices
- **Analytics & Reporting**: Comprehensive intelligence reports

## 💰 Pricing Model

- **Basic Plan**: ₹25,000/month (5 competitors)
- **Professional Plan**: ₹45,000/month (15 competitors)
- **Enterprise Plan**: ₹75,000/month (unlimited competitors)

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/vedantpatil28/blackfang.git
cd blackfang
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set environment variables**
```bash
export DATABASE_URL="postgresql://user:pass@localhost/blackfang"
export JWT_SECRET="your-secret-key"
export ENVIRONMENT="development"
```

4. **Run the application**
```bash
python app.py
```

5. **Access the platform**
- Login: http://localhost:8080/app
- Dashboard: http://localhost:8080/dashboard/1
- API Docs: http://localhost:8080/docs

### Demo Access
- **Email**: demo@blackfangintel.com
- **Password**: demo123

## 📁 Project Structure

```
blackfang-intelligence/
├── app.py                 # Main FastAPI application
├── models.py              # Database models and schemas
├── auth.py                # Authentication and security
├── scraper.py             # Competitive intelligence engine
├── database.py            # Database configuration and utilities
├── config.py              # Application configuration
├── requirements.txt       # Python dependencies
├── Procfile              # Railway deployment configuration
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── dashboard.html    # Main dashboard
│   ├── competitors.html  # Competitor management
│   ├── alerts.html       # Alert management
│   ├── reports.html      # Intelligence reports
│   └── settings.html     # User settings
├── static/               # Static assets
│   ├── css/
│   │   ├── main.css      # Main stylesheet
│   │   ├── dashboard.css # Dashboard styles
│   │   └── components.css# Component styles
│   ├── js/
│   │   ├── app.js        # Main JavaScript
│   │   ├── dashboard.js  # Dashboard functionality
│   │   ├── auth.js       # Authentication handling
│   │   └── components.js # UI components
│   └── images/
│       └── logo.png      # BlackFang logo
├── api/                  # API endpoints
│   ├── __init__.py
│   ├── auth.py           # Authentication endpoints
│   ├── dashboard.py      # Dashboard API
│   ├── competitors.py    # Competitor management
│   └── alerts.py         # Alert management
├── services/             # Business logic services
│   ├── __init__.py
│   ├── intelligence.py   # Intelligence processing
│   ├── scraping.py       # Web scraping service
│   ├── alerts.py         # Alert generation
│   └── reports.py        # Report generation
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── helpers.py        # Helper functions
│   ├── validators.py     # Input validation
│   └── formatters.py     # Data formatting
├── tests/                # Test suite
│   ├── __init__.py
│   ├── test_auth.py      # Authentication tests
│   ├── test_scraper.py   # Scraper tests
│   └── test_api.py       # API tests
└── docs/                 # Documentation
    ├── API.md            # API documentation
    ├── DEPLOYMENT.md     # Deployment guide
    └── BUSINESS.md       # Business model
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/blackfang

# Security
JWT_SECRET=your-super-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Application
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# External Services
SENDGRID_API_KEY=your-sendgrid-key
GOOGLE_PLACES_API_KEY=your-google-key

# Railway Deployment
PORT=8080
HOST=0.0.0.0
```

## 📊 Database Schema

### Companies Table
- User accounts and subscription management
- Authentication and profile information

### Competitors Table
- Competitor profiles and monitoring settings
- Threat levels and priority rankings

### Alerts Table
- Real-time threat notifications
- Strategic recommendations and insights

### Intelligence Data Table
- Raw scraping data and processed insights
- Historical competitive intelligence

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: PBKDF2 with salt for secure password storage
- **Input Validation**: Comprehensive request validation
- **CORS Protection**: Configurable cross-origin request handling
- **Rate Limiting**: API request rate limiting
- **SQL Injection Prevention**: Parameterized queries

## 🚀 Deployment

### Railway.app Deployment

1. **Connect GitHub repository to Railway**
2. **Add PostgreSQL database service**
3. **Configure environment variables**
4. **Deploy automatically from GitHub**

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
python -c "import asyncio; from database import init_database; asyncio.run(init_database())"

# Start the application
uvicorn app:app --host 0.0.0.0 --port 8080
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_auth.py

# Run with coverage
python -m pytest --cov=. tests/
```

## 📈 Business Model

### Target Market
- Automotive dealerships
- Healthcare practices  
- Real estate agencies
- Fitness centers
- Restaurants and hospitality
- E-commerce stores

### Revenue Projections
- **Month 1**: 3 clients = ₹135,000/month
- **Month 3**: 10 clients = ₹450,000/month
- **Month 6**: 25 clients = ₹1,125,000/month
- **Year 1**: 50+ clients = ₹2,250,000+/month

## 📞 Support & Contact

- **Email**: support@blackfangintel.com
- **Website**: https://blackfangintel.com
- **Documentation**: https://docs.blackfangintel.com

## 📄 License

Copyright (c) 2025 BlackFang Intelligence. All rights reserved.

## 🔄 Version History

- **v2.0.0** - Complete production release with professional features
- **v1.0.0** - Initial MVP with basic competitive monitoring