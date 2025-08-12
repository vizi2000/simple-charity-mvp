// API Configuration
const config = {
  development: {
    API_URL: 'http://localhost:8000/api',
    BASE_URL: 'http://localhost:5173'
  },
  production: {
    API_URL: 'http://192.168.100.159/api',
    BASE_URL: 'http://192.168.100.159'
  }
};

// Detect environment
const isProduction = window.location.hostname !== 'localhost' && 
                    window.location.hostname !== '127.0.0.1';

export const API_URL = isProduction ? config.production.API_URL : config.development.API_URL;
export const BASE_URL = isProduction ? config.production.BASE_URL : config.development.BASE_URL;

export default {
  API_URL,
  BASE_URL
};