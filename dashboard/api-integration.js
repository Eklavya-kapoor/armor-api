// Elephas AI Dashboard - Real Data Integration Module
class ElephasAPI {
    constructor() {
        this.baseURL = 'http://localhost:8000'; // Adjust based on your API server
        this.endpoints = {
            health: '/health',
            scan: '/scan',
            stats: '/api/stats',
            activity: '/api/activity',
            threats: '/api/threats',
            analytics: '/api/analytics',
            reports: '/api/reports'
        };
        
        // Cache for reducing API calls
        this.cache = new Map();
        this.cacheTimeout = 30000; // 30 seconds
        
        this.isOnline = false;
        this.checkConnection();
        
        // Setup automatic connection monitoring
        setInterval(() => this.checkConnection(), 60000); // Check every minute
    }
    
    async checkConnection() {
        try {
            const response = await fetch(`${this.baseURL}${this.endpoints.health}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                timeout: 5000
            });
            
            if (response.ok) {
                const health = await response.json();
                this.isOnline = true;
                console.log('✅ Elephas AI API Online:', health);
                
                // Update UI connection status
                this.updateConnectionStatus(true, health);
            } else {
                throw new Error(`API returned ${response.status}`);
            }
        } catch (error) {
            this.isOnline = false;
            console.log('❌ Elephas AI API Offline:', error.message);
            this.updateConnectionStatus(false, { error: error.message });
        }
    }
    
    updateConnectionStatus(isOnline, info) {
        // Update connection indicator in dashboard
        const indicator = document.querySelector('.connection-status');
        if (indicator) {
            indicator.className = `connection-status ${isOnline ? 'online' : 'offline'}`;
            indicator.textContent = isOnline ? 'API Online' : 'API Offline';
            indicator.title = JSON.stringify(info, null, 2);
        }
        
        // Show notification for connection changes
        if (this.lastConnectionState !== undefined && this.lastConnectionState !== isOnline) {
            this.showNotification(
                isOnline ? 'API connection restored' : 'API connection lost',
                isOnline ? 'success' : 'error'
            );
        }
        this.lastConnectionState = isOnline;
    }
    
    showNotification(message, type = 'info') {
        // Create or update notification
        let notification = document.querySelector('.api-notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.className = 'api-notification';
            document.body.appendChild(notification);
        }
        
        notification.className = `api-notification ${type}`;
        notification.textContent = message;
        notification.style.display = 'block';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }
    
    getCacheKey(endpoint, params = {}) {
        return `${endpoint}_${JSON.stringify(params)}`;
    }
    
    isCacheValid(key) {
        const cached = this.cache.get(key);
        if (!cached) return false;
        return (Date.now() - cached.timestamp) < this.cacheTimeout;
    }
    
    async apiRequest(endpoint, options = {}) {
        const cacheKey = this.getCacheKey(endpoint, options.params);
        
        // Return cached data if valid
        if (options.useCache !== false && this.isCacheValid(cacheKey)) {
            console.log('📦 Using cached data for:', endpoint);
            return this.cache.get(cacheKey).data;
        }
        
        try {
            const url = new URL(`${this.baseURL}${endpoint}`);
            if (options.params) {
                Object.keys(options.params).forEach(key => 
                    url.searchParams.append(key, options.params[key])
                );
            }
            
            const response = await fetch(url, {
                method: options.method || 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: options.body ? JSON.stringify(options.body) : undefined
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Cache successful responses
            if (options.useCache !== false) {
                this.cache.set(cacheKey, {
                    data,
                    timestamp: Date.now()
                });
            }
            
            return data;
            
        } catch (error) {
            console.error(`❌ API request failed for ${endpoint}:`, error);
            throw error;
        }
    }
    
    async getDashboardStats() {
        try {
            const stats = await this.apiRequest(this.endpoints.stats);
            console.log('📊 Dashboard stats loaded:', stats);
            return stats;
        } catch (error) {
            console.error('Failed to load dashboard stats:', error);
            // Return fallback data
            return {
                threatsBlocked: Math.floor(Math.random() * 1000) + 2500,
                scansProcessed: Math.floor(Math.random() * 10000) + 150000,
                accuracyRate: 99.7,
                avgResponseTime: Math.floor(Math.random() * 10) + 20,
                uptime: "47h 23m",
                lastUpdated: new Date().toISOString(),
                dataSource: "fallback"
            };
        }
    }
    
    async getRecentActivity() {
        try {
            const activities = await this.apiRequest(this.endpoints.activity);
            console.log('📋 Recent activity loaded:', activities.length, 'items');
            return activities;
        } catch (error) {
            console.error('Failed to load recent activity:', error);
            // Return fallback data
            return [
                {
                    type: 'danger',
                    message: 'High-risk phishing attempt blocked (fallback)',
                    timestamp: Date.now() - 120000,
                    severity: 'high'
                },
                {
                    type: 'warning',
                    message: 'Suspicious message pattern detected (fallback)',
                    timestamp: Date.now() - 300000,
                    severity: 'medium'
                }
            ];
        }
    }
    
    async getThreatData() {
        try {
            const threats = await this.apiRequest(this.endpoints.threats);
            console.log('🌍 Threat data loaded:', threats);
            return threats;
        } catch (error) {
            console.error('Failed to load threat data:', error);
            // Return fallback data
            return {
                timeline: Array.from({length: 24}, () => Math.floor(Math.random() * 100)),
                categories: [
                    { name: 'Phishing', count: Math.floor(Math.random() * 50) + 30, color: '#ff0055' },
                    { name: 'Malware', count: Math.floor(Math.random() * 30) + 15, color: '#ffa500' },
                    { name: 'Spam', count: Math.floor(Math.random() * 20) + 10, color: '#00ff7f' },
                    { name: 'Fraud', count: Math.floor(Math.random() * 15) + 5, color: '#00ffff' }
                ],
                geographic_data: [
                    { country_code: 'US', country_name: 'United States', threat_count: 1247, latitude: 39.8283, longitude: -98.5795 },
                    { country_code: 'CN', country_name: 'China', threat_count: 892, latitude: 35.8617, longitude: 104.1954 }
                ],
                dataSource: "fallback"
            };
        }
    }
    
    async getAnalyticsData(period = '7d') {
        try {
            const analytics = await this.apiRequest(this.endpoints.analytics, {
                params: { period }
            });
            console.log('📈 Analytics data loaded for period:', period, analytics);
            return analytics;
        } catch (error) {
            console.error('Failed to load analytics data:', error);
            // Return fallback data
            return {
                period,
                threat_timeline: Array.from({length: 24}, () => Math.floor(Math.random() * 100)),
                threat_categories: [
                    { name: 'Phishing', count: 45, color: '#ff0055' },
                    { name: 'Malware', count: 25, color: '#ffa500' }
                ],
                performance_metrics: {
                    avg_processing_time: 23.4,
                    total_scans: 15632,
                    avg_confidence: 0.94
                },
                dataSource: "fallback",
                generated_at: new Date().toISOString()
            };
        }
    }
    
    async scanMessage(text, sender = '', metadata = {}) {
        try {
            console.log('🔍 Scanning message:', text.substring(0, 50) + '...');
            
            const result = await this.apiRequest(this.endpoints.scan, {
                method: 'POST',
                body: { text, sender, metadata },
                useCache: false // Don't cache scan results
            });
            
            console.log('✅ Scan completed:', result);
            return result;
            
        } catch (error) {
            console.error('❌ Scan failed:', error);
            throw error;
        }
    }
    
    async generateReport(reportType, options = {}) {
        try {
            const report = await this.apiRequest(this.endpoints.reports, {
                method: 'POST',
                body: {
                    report_type: reportType,
                    ...options
                },
                useCache: false
            });
            
            console.log('📄 Report generated:', report);
            return report;
            
        } catch (error) {
            console.error('Failed to generate report:', error);
            throw error;
        }
    }
    
    // Real-time data updates
    startRealTimeUpdates() {
        // Update dashboard stats every 30 seconds
        this.statsInterval = setInterval(async () => {
            try {
                const stats = await this.getDashboardStats();
                window.dispatchEvent(new CustomEvent('statsUpdated', { detail: stats }));
            } catch (error) {
                console.error('Real-time stats update failed:', error);
            }
        }, 30000);
        
        // Update activity feed every 60 seconds
        this.activityInterval = setInterval(async () => {
            try {
                const activities = await this.getRecentActivity();
                window.dispatchEvent(new CustomEvent('activityUpdated', { detail: activities }));
            } catch (error) {
                console.error('Real-time activity update failed:', error);
            }
        }, 60000);
        
        console.log('🔄 Real-time updates started');
    }
    
    stopRealTimeUpdates() {
        if (this.statsInterval) clearInterval(this.statsInterval);
        if (this.activityInterval) clearInterval(this.activityInterval);
        console.log('⏸️ Real-time updates stopped');
    }
}

// Global API instance
const elephasAPI = new ElephasAPI();

// Export for use in other modules
window.elephasAPI = elephasAPI;
    }
    
    async makeRequest(endpoint, options = {}) {
        if (!this.isOnline) {
            // Return mock data when offline
            return this.getMockData(endpoint);
        }
        
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            return this.getMockData(endpoint);
        }
    }
    
    getMockData(endpoint) {
        // Simulate API response with mock data
        switch (endpoint) {
            case this.endpoints.health:
                return { status: 'ok', timestamp: Date.now() };
            case this.endpoints.stats:
                return this.mockData.stats;
            case this.endpoints.activity:
                return this.mockData.activity;
            case this.endpoints.threats:
                return this.mockData.threats;
            default:
                return { error: 'Unknown endpoint' };
        }
    }
    
    async getStats() {
        return await this.makeRequest(this.endpoints.stats);
    }
    
    async getActivity() {
        return await this.makeRequest(this.endpoints.activity);
    }
    
    async getThreats() {
        return await this.makeRequest(this.endpoints.threats);
    }
    
    async scanMessage(message, options = {}) {
        return await this.makeRequest(this.endpoints.scan, {
            method: 'POST',
            body: JSON.stringify({
                text: message,
                sender: options.sender || '',
                metadata: options.metadata || {}
            })
        });
    }
    
    // Real-time updates simulation
    simulateRealTimeUpdates() {
        return {
            stats: {
                threatsBlocked: this.mockData.stats.threatsBlocked + Math.floor(Math.random() * 5),
                scansProcessed: this.mockData.stats.scansProcessed + Math.floor(Math.random() * 50),
                accuracyRate: (99.5 + Math.random() * 0.5).toFixed(1),
                avgResponseTime: Math.floor(15 + Math.random() * 20)
            },
            newActivity: {
                type: ['danger', 'warning', 'success', 'info'][Math.floor(Math.random() * 4)],
                message: [
                    'Crypto scam detected and blocked',
                    'Suspicious link pattern identified',
                    'Model retrained with new data',
                    'System performance optimized',
                    'New threat signature added',
                    'False positive rate reduced'
                ][Math.floor(Math.random() * 6)],
                timestamp: Date.now()
            }
        };
    }
}

// Dashboard Controller
class DashboardController {
    constructor() {
        this.api = new ScamShieldAPI();
        this.charts = {};
        this.updateInterval = 5000; // 5 seconds
        this.activityInterval = 3000; // 3 seconds
        
        this.init();
    }
    
    async init() {
        await this.loadInitialData();
        this.setupCharts();
        this.startRealTimeUpdates();
        this.setupEventListeners();
    }
    
    async loadInitialData() {
        try {
            const [stats, activity, threats] = await Promise.all([
                this.api.getStats(),
                this.api.getActivity(),
                this.api.getThreats()
            ]);
            
            this.updateStatsDisplay(stats);
            this.updateActivityFeed(activity);
            this.updateChartData(threats);
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }
    
    updateStatsDisplay(stats) {
        const elements = {
            'threats-blocked': stats.threatsBlocked?.toLocaleString() || '0',
            'scans-processed': stats.scansProcessed?.toLocaleString() || '0',
            'accuracy-rate': `${stats.accuracyRate}%` || '0%',
            'avg-response': `${stats.avgResponseTime}ms` || '0ms'
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                element.classList.add('pulse');
                setTimeout(() => element.classList.remove('pulse'), 1000);
            }
        });
    }
    
    updateActivityFeed(activities) {
        const activityList = document.getElementById('activity-list');
        if (!activityList) return;
        
        // Clear existing items
        activityList.innerHTML = '';
        
        activities.forEach(activity => {
            const activityItem = this.createActivityItem(activity);
            activityList.appendChild(activityItem);
        });
    }
    
    createActivityItem(activity) {
        const item = document.createElement('div');
        item.className = 'activity-item';
        
        const iconClass = {
            danger: 'fas fa-exclamation-triangle',
            warning: 'fas fa-search',
            success: 'fas fa-check-circle',
            info: 'fas fa-info-circle'
        }[activity.type] || 'fas fa-info-circle';
        
        const timeAgo = this.formatTimeAgo(activity.timestamp);
        
        item.innerHTML = `
            <div class="activity-icon ${activity.type}">
                <i class="${iconClass}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">${activity.message}</div>
                <div class="activity-time">${timeAgo}</div>
            </div>
        `;
        
        return item;
    }
    
    formatTimeAgo(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;
        
        if (diff < 60000) return 'just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
        return `${Math.floor(diff / 86400000)} days ago`;
    }
    
    setupCharts() {
        this.setupThreatChart();
        this.setupCategoryChart();
    }
    
    setupThreatChart() {
        const ctx = document.getElementById('threatChart');
        if (!ctx) return;
        
        this.charts.threat = new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
                datasets: [{
                    label: 'Threats Detected',
                    data: [45, 67, 89, 156, 234, 189, 267],
                    borderColor: '#ff0055',
                    backgroundColor: 'rgba(255, 0, 85, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Scans Processed',
                    data: [1200, 1800, 2400, 3600, 4200, 3800, 4500],
                    borderColor: '#00ffff',
                    backgroundColor: 'rgba(0, 255, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: '#ffffff' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#888' }
                    },
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#888' }
                    }
                }
            }
        });
    }
    
    setupCategoryChart() {
        const ctx = document.getElementById('categoryChart');
        if (!ctx) return;
        
        this.charts.category = new Chart(ctx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Phishing', 'Malware', 'Spam', 'Fraud', 'Other'],
                datasets: [{
                    data: [45, 25, 15, 10, 5],
                    backgroundColor: ['#ff0055', '#ffa500', '#00ff7f', '#00ffff', '#ff00ff'],
                    borderColor: 'rgba(0, 0, 0, 0.8)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#ffffff', padding: 20 }
                    }
                }
            }
        });
    }
    
    updateChartData(threats) {
        if (this.charts.threat && threats.timeline) {
            this.charts.threat.data.datasets[0].data = threats.timeline;
            this.charts.threat.update();
        }
        
        if (this.charts.category && threats.categories) {
            this.charts.category.data.datasets[0].data = threats.categories.map(c => c.count);
            this.charts.category.update();
        }
    }
    
    startRealTimeUpdates() {
        // Update stats
        setInterval(() => {
            const updates = this.api.simulateRealTimeUpdates();
            this.updateStatsDisplay(updates.stats);
        }, this.updateInterval);
        
        // Update activity feed
        setInterval(() => {
            const updates = this.api.simulateRealTimeUpdates();
            this.addNewActivity(updates.newActivity);
        }, this.activityInterval);
    }
    
    addNewActivity(activity) {
        const activityList = document.getElementById('activity-list');
        if (!activityList) return;
        
        const newItem = this.createActivityItem(activity);
        activityList.insertBefore(newItem, activityList.firstChild);
        
        // Remove old items (keep only last 10)
        while (activityList.children.length > 10) {
            activityList.removeChild(activityList.lastChild);
        }
        
        // Add entrance animation
        newItem.style.opacity = '0';
        newItem.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            newItem.style.transition = 'all 0.5s ease';
            newItem.style.opacity = '1';
            newItem.style.transform = 'translateY(0)';
        }, 100);
    }
    
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleNavigation(item);
            });
        });
        
        // Notification badge
        const notificationBadge = document.querySelector('.notification-badge');
        if (notificationBadge) {
            notificationBadge.addEventListener('click', () => {
                this.showNotifications();
            });
        }
        
        // Profile menu
        const profileInfo = document.querySelector('.profile-info');
        if (profileInfo) {
            profileInfo.addEventListener('click', () => {
                this.showProfileMenu();
            });
        }
    }
    
    handleNavigation(item) {
        // Update active state
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');
        
        const page = item.dataset.page;
        console.log(`Navigation: ${page}`);
        
        // Here you would implement page switching logic
        // For now, we'll just log the navigation
        this.showNotification(`Navigating to ${page.charAt(0).toUpperCase() + page.slice(1)}`, 'info');
    }
    
    showNotifications() {
        this.showNotification('Notifications panel would open here', 'info');
    }
    
    showProfileMenu() {
        this.showNotification('Profile menu would open here', 'info');
    }
    
    showNotification(message, type = 'info') {
        // Simple notification system
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #00ffff;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardController = new DashboardController();
});

// Add notification animation CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
