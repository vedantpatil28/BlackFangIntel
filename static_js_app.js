/**
 * BlackFang Intelligence - Main JavaScript Application
 * Version: 2.0.0
 */

// Global application namespace
window.BlackFang = {
    version: '2.0.0',
    initialized: false,
    config: {},
    utils: {},
    components: {},
    api: {}
};

// Application Configuration
BlackFang.config = {
    apiBase: window.BlackFangConfig?.apiBase || '',
    version: window.BlackFangConfig?.version || '2.0.0',
    environment: window.BlackFangConfig?.environment || 'production',
    demoMode: window.BlackFangConfig?.demoMode || false,
    
    // API endpoints
    endpoints: {
        auth: {
            login: '/api/auth/login',
            logout: '/api/auth/logout',
            refresh: '/api/auth/refresh',
            register: '/api/auth/register',
            me: '/api/auth/me'
        },
        dashboard: {
            data: '/api/dashboard',
            stats: '/api/dashboard/stats'
        },
        competitors: {
            list: '/api/competitors',
            create: '/api/competitors',
            update: '/api/competitors',
            delete: '/api/competitors'
        },
        alerts: {
            list: '/api/alerts',
            markRead: '/api/alerts/read',
            archive: '/api/alerts/archive'
        }
    },
    
    // Storage keys
    storage: {
        accessToken: 'blackfang_access_token',
        refreshToken: 'blackfang_refresh_token',
        userData: 'blackfang_user_data',
        tokenExpires: 'blackfang_token_expires'
    },
    
    // Default settings
    settings: {
        autoRefreshInterval: 300000, // 5 minutes
        requestTimeout: 30000, // 30 seconds
        maxRetries: 3,
        debounceDelay: 300
    }
};

// Utility Functions
BlackFang.utils = {
    
    /**
     * Show loading state globally
     */
    showLoading: function(show = true) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    },
    
    /**
     * Format currency in Indian Rupees
     */
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 0
        }).format(amount);
    },
    
    /**
     * Format relative time
     */
    formatTimeAgo: function(timestamp) {
        const now = new Date();
        const date = new Date(timestamp);
        const diffMs = now - date;
        
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minutes ago`;
        if (diffHours < 24) return `${diffHours} hours ago`;
        if (diffDays < 30) return `${diffDays} days ago`;
        
        return date.toLocaleDateString('en-IN');
    },
    
    /**
     * Format date for display
     */
    formatDate: function(timestamp) {
        return new Date(timestamp).toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    /**
     * Debounce function calls
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Generate unique ID
     */
    generateId: function() {
        return Math.random().toString(36).substr(2, 9);
    },
    
    /**
     * Validate email format
     */
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    /**
     * Copy text to clipboard
     */
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            return navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            return Promise.resolve(successful);
        }
    },
    
    /**
     * Show toast notification
     */
    showToast: function(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Add toast styles if not present
        if (!document.querySelector('#toast-styles')) {
            const styles = document.createElement('style');
            styles.id = 'toast-styles';
            styles.textContent = `
                .toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 16px 20px;
                    border-radius: 8px;
                    color: white;
                    z-index: 10000;
                    max-width: 400px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    animation: slideInRight 0.3s ease-out;
                }
                .toast-info { background: #3b82f6; }
                .toast-success { background: #10b981; }
                .toast-warning { background: #f59e0b; }
                .toast-error { background: #dc2626; }
                .toast-content {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 12px;
                }
                .toast-close {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 18px;
                    cursor: pointer;
                    padding: 0;
                    opacity: 0.8;
                }
                .toast-close:hover { opacity: 1; }
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(toast);
        
        // Auto remove toast
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.animation = 'slideInRight 0.3s ease-out reverse';
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    }
};

// API Manager
BlackFang.api = {
    
    /**
     * Get authentication headers
     */
    getHeaders: function() {
        const token = localStorage.getItem(BlackFang.config.storage.accessToken);
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
        
        if (token) {
            headers.Authorization = `Bearer ${token}`;
        }
        
        return headers;
    },
    
    /**
     * Make API request with error handling
     */
    request: async function(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: this.getHeaders(),
            timeout: BlackFang.config.settings.requestTimeout
        };
        
        const requestOptions = { ...defaultOptions, ...options };
        
        // Add timeout support
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), requestOptions.timeout);
        requestOptions.signal = controller.signal;
        
        try {
            const response = await fetch(BlackFang.config.apiBase + url, requestOptions);
            clearTimeout(timeoutId);
            
            // Handle token expiration
            if (response.status === 401) {
                await this.handleTokenExpiration();
                throw new Error('Authentication required');
            }
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            
            throw error;
        }
    },
    
    /**
     * Handle token expiration
     */
    handleTokenExpiration: async function() {
        const refreshToken = localStorage.getItem(BlackFang.config.storage.refreshToken);
        
        if (refreshToken) {
            try {
                const response = await fetch(BlackFang.config.apiBase + BlackFang.config.endpoints.auth.refresh, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_token: refreshToken })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem(BlackFang.config.storage.accessToken, data.access_token);
                    localStorage.setItem(BlackFang.config.storage.tokenExpires, Date.now() + (data.expires_in * 1000));
                    return;
                }
            } catch (error) {
                console.error('Token refresh failed:', error);
            }
        }
        
        // Clear authentication and redirect to login
        this.clearAuth();
        window.location.href = '/app';
    },
    
    /**
     * Clear authentication data
     */
    clearAuth: function() {
        Object.values(BlackFang.config.storage).forEach(key => {
            localStorage.removeItem(key);
        });
    },
    
    /**
     * Check if user is authenticated
     */
    isAuthenticated: function() {
        const token = localStorage.getItem(BlackFang.config.storage.accessToken);
        const expires = localStorage.getItem(BlackFang.config.storage.tokenExpires);
        
        if (!token || !expires) return false;
        
        return Date.now() < parseInt(expires);
    },
    
    /**
     * Authentication methods
     */
    auth: {
        login: async function(email, password) {
            const response = await BlackFang.api.request(BlackFang.config.endpoints.auth.login, {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });
            
            if (response.success) {
                // Store authentication data
                localStorage.setItem(BlackFang.config.storage.accessToken, response.access_token);
                if (response.refresh_token) {
                    localStorage.setItem(BlackFang.config.storage.refreshToken, response.refresh_token);
                }
                localStorage.setItem(BlackFang.config.storage.userData, JSON.stringify(response.user));
                localStorage.setItem(BlackFang.config.storage.tokenExpires, Date.now() + (response.expires_in * 1000));
            }
            
            return response;
        },
        
        logout: async function() {
            try {
                await BlackFang.api.request(BlackFang.config.endpoints.auth.logout, {
                    method: 'POST'
                });
            } catch (error) {
                console.error('Logout error:', error);
            } finally {
                BlackFang.api.clearAuth();
            }
        },
        
        getCurrentUser: async function() {
            return await BlackFang.api.request(BlackFang.config.endpoints.auth.me);
        }
    },
    
    /**
     * Dashboard methods
     */
    dashboard: {
        getData: async function(companyId) {
            return await BlackFang.api.request(`${BlackFang.config.endpoints.dashboard.data}/${companyId}`);
        }
    },
    
    /**
     * Competitors methods
     */
    competitors: {
        list: async function(companyId) {
            return await BlackFang.api.request(`${BlackFang.config.endpoints.competitors.list}?company_id=${companyId}`);
        },
        
        create: async function(competitorData) {
            return await BlackFang.api.request(BlackFang.config.endpoints.competitors.create, {
                method: 'POST',
                body: JSON.stringify(competitorData)
            });
        },
        
        update: async function(competitorId, updates) {
            return await BlackFang.api.request(`${BlackFang.config.endpoints.competitors.update}/${competitorId}`, {
                method: 'PUT',
                body: JSON.stringify(updates)
            });
        },
        
        delete: async function(competitorId) {
            return await BlackFang.api.request(`${BlackFang.config.endpoints.competitors.delete}/${competitorId}`, {
                method: 'DELETE'
            });
        }
    },
    
    /**
     * Alerts methods
     */
    alerts: {
        list: async function(companyId, options = {}) {
            const params = new URLSearchParams({
                company_id: companyId,
                ...options
            });
            return await BlackFang.api.request(`${BlackFang.config.endpoints.alerts.list}?${params}`);
        },
        
        markRead: async function(alertIds) {
            return await BlackFang.api.request(BlackFang.config.endpoints.alerts.markRead, {
                method: 'POST',
                body: JSON.stringify({ alert_ids: alertIds })
            });
        },
        
        archive: async function(alertIds) {
            return await BlackFang.api.request(BlackFang.config.endpoints.alerts.archive, {
                method: 'POST',
                body: JSON.stringify({ alert_ids: alertIds })
            });
        }
    }
};

// Component System
BlackFang.components = {
    
    /**
     * Initialize all components on page
     */
    init: function() {
        // Auto-refresh components
        this.initAutoRefresh();
        
        // Form components
        this.initForms();
        
        // Navigation components
        this.initNavigation();
        
        // Modal components
        this.initModals();
        
        console.log('🎯 BlackFang components initialized');
    },
    
    /**
     * Auto-refresh functionality
     */
    initAutoRefresh: function() {
        const refreshElements = document.querySelectorAll('[data-auto-refresh]');
        
        refreshElements.forEach(element => {
            const interval = parseInt(element.dataset.autoRefresh) || BlackFang.config.settings.autoRefreshInterval;
            const endpoint = element.dataset.refreshEndpoint;
            
            if (endpoint) {
                setInterval(async () => {
                    try {
                        const data = await BlackFang.api.request(endpoint);
                        element.dispatchEvent(new CustomEvent('dataRefresh', { detail: data }));
                    } catch (error) {
                        console.error('Auto-refresh error:', error);
                    }
                }, interval);
            }
        });
    },
    
    /**
     * Form handling
     */
    initForms: function() {
        const forms = document.querySelectorAll('[data-blackfang-form]');
        
        forms.forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                const action = form.dataset.blackfangForm;
                
                try {
                    BlackFang.utils.showLoading(true);
                    
                    let response;
                    switch (action) {
                        case 'login':
                            response = await BlackFang.api.auth.login(data.email, data.password);
                            if (response.success) {
                                BlackFang.utils.showToast('Login successful!', 'success');
                                window.location.href = `/dashboard/${response.user.id}`;
                            }
                            break;
                        
                        case 'register':
                            response = await BlackFang.api.request('/api/auth/register', {
                                method: 'POST',
                                body: JSON.stringify(data)
                            });
                            if (response.success) {
                                BlackFang.utils.showToast('Registration successful!', 'success');
                                window.location.href = '/app';
                            }
                            break;
                        
                        default:
                            console.warn('Unknown form action:', action);
                    }
                    
                } catch (error) {
                    console.error('Form submission error:', error);
                    BlackFang.utils.showToast(error.message || 'Form submission failed', 'error');
                } finally {
                    BlackFang.utils.showLoading(false);
                }
            });
        });
    },
    
    /**
     * Navigation handling
     */
    initNavigation: function() {
        // Mobile menu toggle
        const mobileToggle = document.querySelector('.mobile-menu-toggle');
        const mobileMenu = document.querySelector('.mobile-menu');
        
        if (mobileToggle && mobileMenu) {
            mobileToggle.addEventListener('click', () => {
                mobileMenu.classList.toggle('active');
            });
        }
        
        // Active nav highlighting
        const navLinks = document.querySelectorAll('.nav-item');
        const currentPath = window.location.pathname;
        
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    },
    
    /**
     * Modal handling
     */
    initModals: function() {
        const modalTriggers = document.querySelectorAll('[data-modal-trigger]');
        
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.dataset.modalTrigger;
                this.openModal(modalId);
            });
        });
        
        // Close modals on overlay click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.closeModal(e.target.querySelector('.modal').id);
            }
        });
        
        // Close modals on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.active');
                if (openModal) {
                    this.closeModal(openModal.id);
                }
            }
        });
    },
    
    /**
     * Open modal
     */
    openModal: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.classList.add('modal-open');
        }
    },
    
    /**
     * Close modal
     */
    closeModal: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.classList.remove('modal-open');
        }
    }
};

// Application Initialization
BlackFang.init = function() {
    if (this.initialized) return;
    
    console.log(`🚀 Initializing BlackFang Intelligence v${this.version}`);
    
    // Initialize components
    this.components.init();
    
    // Set up global error handling
    window.addEventListener('error', (e) => {
        console.error('Global JavaScript error:', e.error);
        if (BlackFang.config.environment === 'development') {
            BlackFang.utils.showToast('JavaScript error occurred', 'error');
        }
    });
    
    // Set up authentication check for protected pages
    if (document.body.classList.contains('protected-page')) {
        if (!this.api.isAuthenticated()) {
            window.location.href = '/app';
            return;
        }
    }
    
    this.initialized = true;
    console.log('✅ BlackFang Intelligence initialized successfully');
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => BlackFang.init());
} else {
    BlackFang.init();
}

// Export to global scope
window.BlackFang = BlackFang;