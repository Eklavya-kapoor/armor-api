/* Cloud Run Dashboard Integration */
/* File: dashboard/cloud-run-config.js */

// ✅ Production API configuration for Cloud Run
const API_CONFIG = {
  // Your Cloud Run service URL
  BASE_URL: 'https://elephas-ai-xxxxxxx-uc.a.run.app',
  
  // Dashboard endpoints
  ENDPOINTS: {
    health: '/health',
    scan: '/scan',
    stats: '/api/stats',
    activity: '/api/activity',
    threats: '/api/threats',
    analytics: '/api/analytics'
  },
  
  // Performance settings
  TIMEOUT: 30000,  // 30 seconds (much faster than Render)
  RETRY_ATTEMPTS: 3,
  CACHE_DURATION: 30000  // 30 seconds cache
};

// ✅ Enhanced API client for Cloud Run
class CloudRunApiClient {
  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
    this.cache = new Map();
  }

  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const cacheKey = `${endpoint}_${JSON.stringify(options)}`;
    
    // Check cache first
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < API_CONFIG.CACHE_DURATION) {
        return cached.data;
      }
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        signal: AbortSignal.timeout(API_CONFIG.TIMEOUT)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Cache successful responses
      this.cache.set(cacheKey, {
        data,
        timestamp: Date.now()
      });

      return data;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // ✅ Scam detection with no hibernation delays
  async scanMessage(text, sender = '', metadata = {}) {
    return this.makeRequest(API_CONFIG.ENDPOINTS.scan, {
      method: 'POST',
      body: JSON.stringify({ text, sender, metadata })
    });
  }

  // ✅ Real-time dashboard stats
  async getDashboardStats() {
    return this.makeRequest(API_CONFIG.ENDPOINTS.stats);
  }

  // ✅ Live activity monitoring
  async getRecentActivity() {
    return this.makeRequest(API_CONFIG.ENDPOINTS.activity);
  }

  // ✅ Threat analytics
  async getThreatData() {
    return this.makeRequest(API_CONFIG.ENDPOINTS.threats);
  }
}

// ✅ Global API client instance
const api = new CloudRunApiClient();

// ✅ Dashboard auto-refresh with Cloud Run
function initializeDashboard() {
  // Update stats every 10 seconds (no hibernation worry!)
  setInterval(async () => {
    try {
      const stats = await api.getDashboardStats();
      updateDashboardUI(stats);
    } catch (error) {
      console.error('Failed to update dashboard:', error);
    }
  }, 10000);

  // Update activity every 15 seconds
  setInterval(async () => {
    try {
      const activity = await api.getRecentActivity();
      updateActivityFeed(activity);
    } catch (error) {
      console.error('Failed to update activity:', error);
    }
  }, 15000);
}

// Start dashboard when page loads
document.addEventListener('DOMContentLoaded', initializeDashboard);
