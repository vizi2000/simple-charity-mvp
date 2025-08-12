import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'

console.log('Main.jsx loading...');

function TestApp() {
  console.log('TestApp rendering...');
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>React is working!</h1>
      <p>Hostname: {window.location.hostname}</p>
      <p>Path: {window.location.pathname}</p>
      <p>If you see this, React loaded successfully.</p>
    </div>
  );
}

try {
  console.log('Looking for root element...');
  const rootElement = document.getElementById('root');
  console.log('Root element:', rootElement);
  
  if (rootElement) {
    console.log('Creating React root...');
    ReactDOM.createRoot(rootElement).render(
      <React.StrictMode>
        <TestApp />
      </React.StrictMode>
    );
    console.log('React app rendered!');
  } else {
    console.error('Root element not found!');
  }
} catch (error) {
  console.error('Error rendering React app:', error);
}