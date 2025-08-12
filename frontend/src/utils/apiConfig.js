// API configuration helper
export const getApiBase = () => {
  const { hostname, protocol } = window.location;
  
  if (hostname === 'borgtools.ddns.net') {
    return `${protocol}//borgtools.ddns.net/bramkamvp/api`;
  } else if (hostname === '192.168.100.159') {
    return `${protocol}//${hostname}/api`;
  } else {
    // Local development
    return '/api';
  }
};

// Helper to build full API URL
export const apiUrl = (path) => {
  const base = getApiBase();
  return `${base}${path}`;
};

export default { getApiBase, apiUrl };