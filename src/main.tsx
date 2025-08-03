import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import serviceWorkerManager from './utils/serviceWorker'
import performanceMonitor from './utils/performance'

// Initialize Service Worker
if ('serviceWorker' in navigator) {
  serviceWorkerManager.register().then((registered) => {
    if (registered) {
      console.log('Service Worker registered successfully');
    }
  });
}

// Initialize Performance Monitoring
performanceMonitor.addObserver((metrics) => {
  console.log('Performance metrics collected:', metrics);
  
  // Send metrics to backend
  fetch('/api/v1/performance/metrics', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(metrics)
  }).catch(error => {
    console.error('Failed to send performance metrics:', error);
  });
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
