// API utility functions with dynamic URL configuration

const getApiUrl = () => {
  const { protocol, hostname } = window.location;
  
  if (hostname === 'borgtools.ddns.net') {
    return `${protocol}//${hostname}/bramkamvp/api`;
  } else if (hostname === '192.168.100.159') {
    return `${protocol}//${hostname}/api`;
  } else {
    // Local development - use relative URLs
    return '/api';
  }
};

export const API_BASE = getApiUrl();

// Helper function for API calls
export const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    throw new Error(`API call failed: ${response.status}`);
  }
  
  return response.json();
};

// Specific API endpoints
export const API = {
  organization: () => `${API_BASE}/organization`,
  organizationStats: () => `${API_BASE}/organization/stats`,
  organizationGoal: (goalId) => `${API_BASE}/organization/goal/${goalId}`,
  paymentsInitiate: () => `${API_BASE}/payments/initiate`,
  paymentStatus: (paymentId) => `${API_BASE}/payments/${paymentId}/status`,
  paymentFormData: (paymentId) => `${API_BASE}/payments/${paymentId}/form-data`,
  paymentProcessMock: (paymentId) => `${API_BASE}/payments/${paymentId}/process-mock`,
};

export default API;