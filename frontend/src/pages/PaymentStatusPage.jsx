import React, { useEffect, useState } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { ArrowPathIcon } from '@heroicons/react/24/outline'

export default function PaymentStatusPage() {
  const { paymentId } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [checking, setChecking] = useState(true)
  const [paymentData, setPaymentData] = useState(null)
  
  const result = searchParams.get('result')
  
  useEffect(() => {
    checkPaymentStatus()
  }, [])
  
  const checkPaymentStatus = async () => {
    try {
      // Get payment status from backend
      const response = await fetch(`/api/payments/${paymentId}/status`)
      
      if (response.ok) {
        const data = await response.json()
        setPaymentData(data)
        
        // Redirect based on status
        if (data.status === 'completed' || result === 'success') {
          navigate(`/dziekujemy?amount=${data.amount}`)
        } else if (data.status === 'failed' || result === 'failure') {
          setChecking(false)
        } else {
          // Still pending, check again in a few seconds
          setTimeout(checkPaymentStatus, 3000)
        }
      } else {
        setChecking(false)
      }
    } catch (error) {
      console.error('Error checking payment status:', error)
      setChecking(false)
    }
  }
  
  return (
    <Layout>
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          {checking ? (
            <>
              <ArrowPathIcon className="h-16 w-16 mx-auto mb-4 text-primary animate-spin" />
              <h2 className="text-2xl font-bold mb-2">Sprawdzanie statusu płatności...</h2>
              <p className="text-gray-600">Proszę czekać, weryfikujemy Twoją płatność.</p>
            </>
          ) : (
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
        </div>
      </div>
    </Layout>
  )
}