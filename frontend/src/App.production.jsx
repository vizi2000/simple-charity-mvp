import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import GoalPage from './pages/GoalPage'
import PaymentPage from './pages/PaymentPage'
import PaymentMethodPage from './pages/PaymentMethodPage'
import PaymentProcessingPage from './pages/PaymentProcessingPage'
import PaymentStatusPage from './pages/PaymentStatusPage'
import ThankYouPage from './pages/ThankYouPage'

function App() {
  // Determine basename based on hostname
  const getBasename = () => {
    const { hostname } = window.location;
    if (hostname === 'borgtools.ddns.net') {
      return '/bramkamvp';
    }
    return '';
  };

  return (
    <Router basename={getBasename()}>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/cel/:goalId" element={<GoalPage />} />
        <Route path="/platnosc/:paymentId" element={<PaymentPage />} />
        <Route path="/platnosc/:paymentId/metoda" element={<PaymentMethodPage />} />
        <Route path="/platnosc/:paymentId/przetwarzanie" element={<PaymentProcessingPage />} />
        <Route path="/platnosc/:paymentId/status" element={<PaymentStatusPage />} />
        <Route path="/dziekujemy" element={<ThankYouPage />} />
      </Routes>
    </Router>
  )
}

export default App