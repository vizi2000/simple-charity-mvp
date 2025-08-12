import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { ArrowPathIcon } from '@heroicons/react/24/outline'

export default function PaymentPage() {
  const { paymentId } = useParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState('checking')
  const [paymentData, setPaymentData] = useState(null)

  useEffect(() => {
    checkPaymentStatus()
    const interval = setInterval(checkPaymentStatus, 3000) // Check every 3 seconds
    
    return () => clearInterval(interval)
  }, [paymentId])

  const checkPaymentStatus = async () => {
    try {
      const response = await fetch(`/api/payments/${paymentId}/status`)
      
      if (!response.ok) {
        setStatus('error')
        return
      }
      
      const data = await response.json()
      setPaymentData(data)
      
      if (data.status === 'completed') {
        // Redirect to thank you page
        setTimeout(() => {
          navigate(`/dziekujemy?amount=${data.amount}`)
        }, 1000)
      } else if (data.status === 'failed' || data.status === 'cancelled') {
        setStatus('failed')
      }
    } catch (error) {
      console.error('Error checking payment status:', error)
      setStatus('error')
    }
  }

  return (
    <Layout>
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          {status === 'checking' && (
            <>
              <ArrowPathIcon className="h-16 w-16 mx-auto mb-4 text-primary animate-spin" />
              <h2 className="text-2xl font-bold mb-2">Przetwarzanie płatności...</h2>
              <p className="text-gray-600">Proszę czekać, sprawdzamy status Twojej płatności.</p>
            </>
          )}
          
          {status === 'failed' && (
            <>
              <div className="text-red-500 mb-4">
                <svg className="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold mb-2">Płatność nieudana</h2>
              <p className="text-gray-600 mb-6">
                Niestety, nie udało się zrealizować płatności. Spróbuj ponownie.
              </p>
              <button
                onClick={() => navigate('/')}
                className="btn-primary"
              >
                Powrót do strony głównej
              </button>
            </>
          )}
          
          {status === 'error' && (
            <>
              <div className="text-yellow-500 mb-4">
                <svg className="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold mb-2">Błąd</h2>
              <p className="text-gray-600 mb-6">
                Wystąpił błąd podczas sprawdzania statusu płatności.
              </p>
              <button
                onClick={() => navigate('/')}
                className="btn-primary"
              >
                Powrót do strony głównej
              </button>
            </>
          )}
        </div>
      </div>
    </Layout>
  )
}