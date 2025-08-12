import React, { useState, useEffect } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { CheckCircleIcon, XCircleIcon, ClockIcon } from '@heroicons/react/24/outline'

export default function PaymentStatusPage() {
  const { paymentId } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [verificationStatus, setVerificationStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [retryCount, setRetryCount] = useState(0)
  
  // Get order ID from URL params
  const orderId = searchParams.get('oid')
  const urlStatus = window.location.pathname.includes('success') ? 'success' : 'failure'

  // API URL configuration
  const getApiUrl = (path) => {
    if (window.location.hostname === 'borgtools.ddns.net') {
      return `https://borgtools.ddns.net/bramkamvp/api${path}`;
    }
    return `/api${path}`;
  };

  useEffect(() => {
    verifyPaymentStatus()
  }, [paymentId, orderId])

  useEffect(() => {
    // Auto-refresh for pending payments
    if (verificationStatus?.is_pending && retryCount < 10) {
      const timer = setTimeout(() => {
        setRetryCount(prev => prev + 1)
        verifyPaymentStatus()
      }, 3000) // Check every 3 seconds
      
      return () => clearTimeout(timer)
    }
  }, [verificationStatus, retryCount])

  const verifyPaymentStatus = async () => {
    try {
      // IMPORTANT: Never trust URL parameters for payment status!
      // Always verify with backend which checks S2S notifications
      
      const verifyUrl = getApiUrl(`/payments/${paymentId || orderId}/verify`)
      const response = await fetch(verifyUrl)
      const data = await response.json()
      
      setVerificationStatus(data)
      
      // Log any discrepancy between URL and actual status
      if (data.verified) {
        const actualStatus = data.is_completed ? 'success' : 
                           data.is_failed ? 'failure' : 'pending'
        
        if (actualStatus !== urlStatus && !data.is_pending) {
          console.warn('URL status does not match actual payment status!', {
            urlStatus,
            actualStatus,
            paymentData: data
          })
        }
      }
    } catch (error) {
      console.error('Error verifying payment:', error)
      setVerificationStatus({
        verified: false,
        status: 'error',
        message: 'Nie można zweryfikować statusu płatności'
      })
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = () => {
    if (!verificationStatus?.verified) {
      return <XCircleIcon className="w-20 h-20 text-red-500 mx-auto" />
    }
    
    if (verificationStatus.is_completed) {
      return <CheckCircleIcon className="w-20 h-20 text-green-500 mx-auto" />
    } else if (verificationStatus.is_failed) {
      return <XCircleIcon className="w-20 h-20 text-red-500 mx-auto" />
    } else {
      return <ClockIcon className="w-20 h-20 text-yellow-500 mx-auto animate-pulse" />
    }
  }

  const getStatusColor = () => {
    if (!verificationStatus?.verified) return 'red'
    if (verificationStatus.is_completed) return 'green'
    if (verificationStatus.is_failed) return 'red'
    return 'yellow'
  }

  if (loading && retryCount === 0) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Weryfikowanie statusu płatności...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-xl shadow-lg p-8">
          {/* Status Icon */}
          <div className="mb-6">
            {getStatusIcon()}
          </div>

          {/* Status Message */}
          <div className="text-center mb-8">
            <h1 className={`text-2xl font-bold mb-4 text-${getStatusColor()}-600`}>
              {verificationStatus?.message || 'Sprawdzanie statusu...'}
            </h1>
            
            {verificationStatus?.verified && (
              <>
                {verificationStatus.is_completed && (
                  <div className="space-y-2">
                    <p className="text-gray-600">
                      Dziękujemy za Twoje wsparcie!
                    </p>
                    <p className="text-sm text-gray-500">
                      Numer zamówienia: {verificationStatus.order_id}
                    </p>
                    {verificationStatus.transaction_id && (
                      <p className="text-sm text-gray-500">
                        ID transakcji: {verificationStatus.transaction_id}
                      </p>
                    )}
                  </div>
                )}
                
                {verificationStatus.is_failed && (
                  <div className="space-y-2">
                    <p className="text-gray-600">
                      Płatność nie została zrealizowana.
                    </p>
                    <p className="text-sm text-gray-500">
                      Możesz spróbować ponownie lub skontaktować się z nami.
                    </p>
                  </div>
                )}
                
                {verificationStatus.is_pending && (
                  <div className="space-y-2">
                    <p className="text-gray-600">
                      Twoja płatność jest obecnie przetwarzana.
                    </p>
                    <p className="text-sm text-gray-500">
                      Strona odświeży się automatycznie...
                    </p>
                    <div className="mt-4">
                      <div className="inline-flex items-center text-sm text-gray-500">
                        <ClockIcon className="w-4 h-4 mr-1 animate-spin" />
                        Sprawdzanie ({retryCount}/10)
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
            
            {!verificationStatus?.verified && (
              <div className="space-y-2">
                <p className="text-gray-600">
                  Nie można zweryfikować płatności.
                </p>
                <p className="text-sm text-gray-500">
                  Prosimy o kontakt jeśli środki zostały pobrane.
                </p>
              </div>
            )}
          </div>

          {/* Security Note */}
          {verificationStatus?.is_completed && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-green-800">
                🔒 Płatność została bezpiecznie przetworzona i potwierdzona przez system bankowy.
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Powrót do strony głównej
            </button>
            
            {verificationStatus?.is_failed && (
              <button
                onClick={() => navigate(-2)}
                className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Spróbuj ponownie
              </button>
            )}
          </div>

          {/* Contact Info */}
          <div className="mt-8 pt-6 border-t border-gray-200 text-center">
            <p className="text-sm text-gray-500">
              Masz pytania? Skontaktuj się z nami:
            </p>
            <p className="text-sm text-gray-600 mt-1">
              📧 kontakt@misjonarze-tarnow.pl | 📱 790 525 400
            </p>
          </div>
        </div>

        {/* Technical Details (for debugging - remove in production) */}
        {process.env.NODE_ENV === 'development' && verificationStatus && (
          <div className="mt-4 p-4 bg-gray-100 rounded text-xs text-gray-600">
            <pre>{JSON.stringify(verificationStatus, null, 2)}</pre>
          </div>
        )}
      </div>
    </Layout>
  )
}