// BlackFang Intelligence Platform JavaScript

// Application Data
const applicationData = {
  "competitors": [
    {
      "id": 1,
      "name": "AutoMax Dealers",
      "website": "cars24.com",
      "threat_level": "HIGH",
      "industry": "Automotive",
      "monitoring_status": "active",
      "location": "Mumbai, Maharashtra",
      "alert_count": 3,
      "last_scraped": "2025-08-24T18:30:00Z"
    },
    {
      "id": 2,
      "name": "Speed Motors",
      "website": "carwale.com",
      "threat_level": "MEDIUM",
      "industry": "Automotive",
      "monitoring_status": "active",
      "location": "Delhi, NCR",
      "alert_count": 2,
      "last_scraped": "2025-08-24T18:25:00Z"
    },
    {
      "id": 3,
      "name": "Elite Auto Solutions",
      "website": "cardekho.com",
      "threat_level": "LOW",
      "industry": "Automotive",
      "monitoring_status": "active",
      "location": "Bangalore, Karnataka",
      "alert_count": 3,
      "last_scraped": "2025-08-24T18:20:00Z"
    }
  ],
  "alerts": [
    {
      "id": 1,
      "competitor_id": 1,
      "competitor_name": "AutoMax Dealers",
      "title": "🔴 CRITICAL: Major Price War Detected",
      "severity": "HIGH",
      "message": "AutoMax Dealers implemented aggressive 8% price reduction on Honda City models (₹95,000 decrease). Market share impact imminent within 48 hours.",
      "recommendation": "IMMEDIATE ACTION: Consider price matching strategy or launch Premium Service Value campaign highlighting superior customer service and warranty benefits.",
      "confidence_score": 0.95,
      "created_at": "2025-08-24T16:30:00Z",
      "is_read": false
    },
    {
      "id": 2,
      "competitor_id": 2,
      "competitor_name": "Speed Motors",
      "title": "🟡 ALERT: Aggressive Marketing Campaign Launch",
      "severity": "MEDIUM",
      "message": "Speed Motors launched comprehensive Monsoon Festival Special campaign: 5% additional discount + Free comprehensive insurance + Extended warranty.",
      "recommendation": "STRATEGIC RESPONSE: Deploy counter-campaign within 72 hours. Consider Exclusive Client Benefits package with added-value services.",
      "confidence_score": 0.87,
      "created_at": "2025-08-24T14:30:00Z",
      "is_read": false
    },
    {
      "id": 3,
      "competitor_id": 3,
      "competitor_name": "Elite Auto Solutions",
      "title": "🟡 OPPORTUNITY: Service Quality Issues",
      "severity": "MEDIUM",
      "message": "Elite Auto Solutions received 4 negative reviews in past 48 hours citing delivery delays and poor after-sales support. Customer sentiment declining (-15%).",
      "recommendation": "MARKET OPPORTUNITY: Target messaging around Reliable Delivery & Premium Support. Launch Satisfaction Guarantee campaign to capture dissatisfied customers.",
      "confidence_score": 0.91,
      "created_at": "2025-08-24T13:30:00Z",
      "is_read": false
    },
    {
      "id": 4,
      "competitor_id": 1,
      "competitor_name": "AutoMax Dealers",
      "title": "🔵 INFO: Inventory Pattern Change",
      "severity": "LOW",
      "message": "AutoMax Dealers showing increased inventory movement on premium SUV models. 23% increase in featured listings over 7 days.",
      "recommendation": "PREPARATION: Review SUV inventory levels and pricing strategy. Potential market demand shift detected.",
      "confidence_score": 0.78,
      "created_at": "2025-08-24T12:30:00Z",
      "is_read": true
    },
    {
      "id": 5,
      "competitor_id": 2,
      "competitor_name": "Speed Motors",
      "title": "🔵 MONITORING: Enhanced Digital Presence",
      "severity": "LOW",
      "message": "Speed Motors expanded social media advertising spend by 40% across Facebook and Instagram. New video marketing campaign launched.",
      "recommendation": "COMPETITIVE RESPONSE: Evaluate digital marketing budget allocation. Consider enhanced social media engagement strategy.",
      "confidence_score": 0.82,
      "created_at": "2025-08-24T11:30:00Z",
      "is_read": true
    },
    {
      "id": 6,
      "competitor_id": 3,
      "competitor_name": "Elite Auto Solutions",
      "title": "🟡 PRODUCT ALERT: Extended Warranty Program",
      "severity": "MEDIUM",
      "message": "Elite Auto Solutions introduced Total Care Protection - 5-year extended warranty program with roadside assistance and maintenance.",
      "recommendation": "SERVICE DIFFERENTIATION: Develop superior warranty program highlighting proven service track record. Create comparison showing service quality advantages.",
      "confidence_score": 0.89,
      "created_at": "2025-08-24T10:30:00Z",
      "is_read": false
    }
  ],
  "statistics": {
    "total_competitors": 3,
    "active_competitors": 3,
    "total_alerts": 8,
    "unread_alerts": 4,
    "high_priority_alerts": 1,
    "medium_priority_alerts": 3,
    "low_priority_alerts": 2,
    "today_alerts": 3,
    "week_alerts": 8
  },
  "user": {
    "id": 1,
    "name": "Demo Automotive Dealership",
    "email": "demo@blackfangintel.com",
    "company_name": "Demo Motors Pvt Ltd",
    "subscription_plan": "professional",
    "monthly_fee": 45000
  }
};

// Application State
let currentUser = null;
let currentSection = 'dashboard';
let alertFilter = 'all';

// DOM Elements
const loginPage = document.getElementById('loginPage');
const mainApp = document.getElementById('mainApp');
const loginForm = document.getElementById('loginForm');
const loginError = document.getElementById('loginError');
const navButtons = document.querySelectorAll('.nav-btn');
const sections = document.querySelectorAll('.main-section');
const logoutBtn = document.getElementById('logoutBtn');
const refreshBtn = document.getElementById('refreshBtn');
const lastUpdateTime = document.getElementById('lastUpdateTime');
const alertBadge = document.getElementById('alertBadge');

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Check if user is logged in (for demo purposes, always start with login)
    showLoginPage();
    
    // Set up event listeners
    setupEventListeners();
    
    // Update last update time
    updateLastUpdateTime();
}

function setupEventListeners() {
    // Login form
    loginForm.addEventListener('submit', handleLogin);
    
    // Navigation
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const section = btn.dataset.section;
            navigateToSection(section);
        });
    });
    
    // Logout
    logoutBtn.addEventListener('click', handleLogout);
    
    // Refresh
    refreshBtn.addEventListener('click', handleRefresh);
    
    // Alert filters
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const filter = btn.dataset.filter;
            setAlertFilter(filter);
        });
    });
    
    // Mark all alerts as read
    const markAllReadBtn = document.getElementById('markAllReadBtn');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', markAllAlertsAsRead);
    }
}

// Authentication Functions
function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    // Demo authentication
    if (email === 'demo@blackfangintel.com' && password === 'demo123') {
        currentUser = applicationData.user;
        showMainApp();
        populateAllData();
    } else {
        showLoginError('Invalid credentials. Please use demo@blackfangintel.com / demo123');
    }
}

function handleLogout() {
    currentUser = null;
    showLoginPage();
    clearLoginForm();
}

function showLoginError(message) {
    loginError.textContent = message;
    loginError.classList.remove('hidden');
}

function clearLoginForm() {
    document.getElementById('email').value = '';
    document.getElementById('password').value = '';
    loginError.classList.add('hidden');
}

// UI State Functions
function showLoginPage() {
    loginPage.classList.remove('hidden');
    mainApp.classList.add('hidden');
}

function showMainApp() {
    loginPage.classList.add('hidden');
    mainApp.classList.remove('hidden');
}

// Navigation Functions
function navigateToSection(sectionName) {
    // Update navigation
    navButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.section === sectionName) {
            btn.classList.add('active');
        }
    });
    
    // Update sections
    sections.forEach(section => {
        section.classList.remove('active');
        if (section.id === sectionName + 'Section') {
            section.classList.add('active');
        }
    });
    
    currentSection = sectionName;
    
    // Populate section-specific data
    if (sectionName === 'competitors') {
        populateCompetitorsList();
    } else if (sectionName === 'alerts') {
        populateAlertsList();
    }
}

// Data Population Functions
function populateAllData() {
    populateDashboard();
    populateCompetitorsList();
    populateAlertsList();
    updateAlertBadge();
}

function populateDashboard() {
    // Populate critical alerts
    const criticalAlertsContainer = document.getElementById('criticalAlerts');
    const criticalAlerts = applicationData.alerts.filter(alert => alert.severity === 'HIGH').slice(0, 2);
    
    criticalAlertsContainer.innerHTML = criticalAlerts.map(alert => `
        <div class="critical-alert">
            <div class="alert-header">
                <h3 class="alert-title">${alert.title}</h3>
                <span class="alert-time">${formatTime(alert.created_at)}</span>
            </div>
            <p class="alert-message">${alert.message}</p>
            <div class="alert-recommendation">
                <strong>Strategic Recommendation:</strong> ${alert.recommendation}
            </div>
            <div class="confidence-score">
                Confidence: ${Math.round(alert.confidence_score * 100)}%
            </div>
        </div>
    `).join('');
    
    // Populate competitor network
    const competitorNetworkContainer = document.getElementById('competitorNetwork');
    competitorNetworkContainer.innerHTML = applicationData.competitors.map(competitor => `
        <div class="competitor-card">
            <div class="competitor-header">
                <h3 class="competitor-name">${competitor.name}</h3>
                <span class="threat-level ${competitor.threat_level}">${competitor.threat_level}</span>
            </div>
            <div class="competitor-details">
                <div class="detail-row">
                    <span>Website:</span>
                    <strong>${competitor.website}</strong>
                </div>
                <div class="detail-row">
                    <span>Location:</span>
                    <strong>${competitor.location}</strong>
                </div>
                <div class="detail-row">
                    <span>Active Alerts:</span>
                    <strong>${competitor.alert_count}</strong>
                </div>
                <div class="detail-row">
                    <span>Last Scraped:</span>
                    <strong>${formatTime(competitor.last_scraped)}</strong>
                </div>
                <div class="detail-row">
                    <span>Status:</span>
                    <strong style="color: #10b981;">Active</strong>
                </div>
            </div>
        </div>
    `).join('');
}

function populateCompetitorsList() {
    const competitorsListContainer = document.getElementById('competitorsList');
    competitorsListContainer.innerHTML = applicationData.competitors.map(competitor => `
        <div class="competitor-card">
            <div class="competitor-header">
                <h3 class="competitor-name">${competitor.name}</h3>
                <span class="threat-level ${competitor.threat_level}">${competitor.threat_level}</span>
            </div>
            <div class="competitor-details">
                <div class="detail-row">
                    <span>Website:</span>
                    <strong>${competitor.website}</strong>
                </div>
                <div class="detail-row">
                    <span>Industry:</span>
                    <strong>${competitor.industry}</strong>
                </div>
                <div class="detail-row">
                    <span>Location:</span>
                    <strong>${competitor.location}</strong>
                </div>
                <div class="detail-row">
                    <span>Active Alerts:</span>
                    <strong>${competitor.alert_count}</strong>
                </div>
                <div class="detail-row">
                    <span>Last Scraped:</span>
                    <strong>${formatTime(competitor.last_scraped)}</strong>
                </div>
                <div class="detail-row">
                    <span>Monitoring:</span>
                    <strong style="color: #10b981;">Active</strong>
                </div>
            </div>
            <div style="margin-top: 16px; display: flex; gap: 8px;">
                <button class="btn btn--outline btn--sm">
                    <i class="fas fa-edit"></i>
                    Edit
                </button>
                <button class="btn btn--outline btn--sm">
                    <i class="fas fa-chart-line"></i>
                    Analytics
                </button>
            </div>
        </div>
    `).join('');
}

function populateAlertsList() {
    const alertsListContainer = document.getElementById('alertsList');
    let filteredAlerts = applicationData.alerts;
    
    if (alertFilter !== 'all') {
        filteredAlerts = applicationData.alerts.filter(alert => alert.severity === alertFilter);
    }
    
    alertsListContainer.innerHTML = filteredAlerts.map(alert => `
        <div class="alert-item ${alert.severity} ${alert.is_read ? 'read' : 'unread'}">
            <div class="alert-header">
                <h3 class="alert-title">${alert.title}</h3>
                <div style="display: flex; gap: 12px; align-items: center;">
                    <span class="alert-time">${formatTime(alert.created_at)}</span>
                    <span class="threat-level ${alert.severity}">${alert.severity}</span>
                </div>
            </div>
            <p class="alert-message"><strong>Competitor:</strong> ${alert.competitor_name}</p>
            <p class="alert-message">${alert.message}</p>
            <div class="alert-recommendation">
                <strong>Strategic Recommendation:</strong> ${alert.recommendation}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px;">
                <div class="confidence-score">
                    Confidence: ${Math.round(alert.confidence_score * 100)}%
                </div>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn--outline btn--sm" onclick="toggleAlertRead(${alert.id})">
                        <i class="fas fa-${alert.is_read ? 'eye-slash' : 'check'}"></i>
                        ${alert.is_read ? 'Mark Unread' : 'Mark Read'}
                    </button>
                    <button class="btn btn--outline btn--sm">
                        <i class="fas fa-share"></i>
                        Share
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Alert Management Functions
function setAlertFilter(filter) {
    alertFilter = filter;
    
    // Update filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.filter === filter) {
            btn.classList.add('active');
        }
    });
    
    // Repopulate alerts list
    populateAlertsList();
}

function toggleAlertRead(alertId) {
    const alert = applicationData.alerts.find(a => a.id === alertId);
    if (alert) {
        alert.is_read = !alert.is_read;
        populateAlertsList();
        updateAlertBadge();
    }
}

function markAllAlertsAsRead() {
    applicationData.alerts.forEach(alert => {
        alert.is_read = true;
    });
    populateAlertsList();
    updateAlertBadge();
}

function updateAlertBadge() {
    const unreadCount = applicationData.alerts.filter(alert => !alert.is_read).length;
    alertBadge.textContent = unreadCount;
    alertBadge.style.display = unreadCount > 0 ? 'block' : 'none';
}

// Utility Functions
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 60) {
        return `${diffInMinutes}m ago`;
    } else if (diffInMinutes < 1440) {
        return `${Math.floor(diffInMinutes / 60)}h ago`;
    } else {
        return date.toLocaleDateString('en-IN', { 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-IN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    if (lastUpdateTime) {
        lastUpdateTime.textContent = timeString;
    }
}

function handleRefresh() {
    // Show refresh animation
    const refreshIcon = refreshBtn.querySelector('i');
    refreshIcon.style.animation = 'spin 1s linear';
    
    // Simulate data refresh
    setTimeout(() => {
        updateLastUpdateTime();
        populateAllData();
        refreshIcon.style.animation = '';
        
        // Show a subtle notification
        showNotification('Data refreshed successfully', 'success');
    }, 1000);
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: type === 'success' ? 'rgba(16, 185, 129, 0.9)' : 'rgba(59, 130, 246, 0.9)',
        color: 'white',
        padding: '12px 20px',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        zIndex: '1000',
        fontSize: '14px',
        fontWeight: '500',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease'
    });
    
    // Add to document
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// CSS Animation for refresh button
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

// Auto-refresh every 5 minutes (for demo purposes)
setInterval(() => {
    if (currentUser && currentSection === 'dashboard') {
        updateLastUpdateTime();
        // In a real application, this would fetch new data from the server
    }
}, 300000); // 5 minutes

// Simulate real-time updates every 30 seconds on dashboard
setInterval(() => {
    if (currentUser && currentSection === 'dashboard') {
        // Simulate minor updates like timestamp changes
        updateLastUpdateTime();
    }
}, 30000); // 30 seconds

// Make functions available globally for onclick handlers
window.toggleAlertRead = toggleAlertRead;