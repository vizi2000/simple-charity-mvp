// Production configuration for borgtools.ddns.net/bramkamvp deployment

const getBaseUrl = () => {
  const { protocol, hostname } = window.location;
  
  // Check if we're on borgtools.ddns.net or local development
  if (hostname === 'borgtools.ddns.net') {
    return `${protocol}//${hostname}/bramkamvp`;
  } else if (hostname === '192.168.100.159') {
    return `${protocol}//${hostname}`;
  } else {
    // Local development
    return 'http://localhost:5174';
  }
};

const getApiUrl = () => {
  const { protocol, hostname } = window.location;
  
  if (hostname === 'borgtools.ddns.net') {
    return `${protocol}//${hostname}/bramkamvp/api`;
  } else if (hostname === '192.168.100.159') {
    return `${protocol}//${hostname}/api`;
  } else {
    // Local development
    return 'http://localhost:8000/api';
  }
};

export const BASE_URL = getBaseUrl();
export const API_URL = getApiUrl();

export default {
  BASE_URL,
  API_URL
};