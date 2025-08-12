import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import Layout from '../components/Layout'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'
import { getAvailablePaymentMethods } from '../utils/deviceDetection'

export default function PaymentMethodPage() {
  const { paymentId } = useParams()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [paymentMethods, setPaymentMethods] = useState([])
  const [selectedMethod, setSelectedMethod] = useState(null)
  const [loading, setLoading] = useState(false)
  
  // Get payment details from URL params
  const amount = searchParams.get('amount')
  const goalName = searchParams.get('goal')
  const goalId = searchParams.get('goalId')

  useEffect(() => {
    // Get device-specific payment methods
    const methods = getAvailablePaymentMethods()
    setPaymentMethods(methods)
    
    // Pre-select primary method if available
    const primaryMethod = methods.find(m => m.primary)
    if (primaryMethod) {
      setSelectedMethod(primaryMethod.id)
    }
  }, [])

  const handleMethodSelect = (methodId) => {
    setSelectedMethod(methodId)
  }

  const handlePayment = async () => {
    if (!selectedMethod) {
      alert('Proszę wybrać metodę płatności')
      return
    }

    setLoading(true)

    // Navigate to processing page with payment details
    navigate(`/platnosc/${paymentId}/przetwarzanie`, {
      state: {
        paymentId,
        amount,
        goalName,
        goalId,
        paymentMethod: selectedMethod
      }
    })
  }

  const formatCurrency = (value) => {
    if (!value) return ''
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
      minimumFractionDigits: 0
    }).format(parseFloat(value))
  }


  return (
    <Layout>
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4 max-w-2xl">
          {/* Back button */}
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6 transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5" />
            <span>Powrót</span>
          </button>

          {/* Payment Summary */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h1 className="text-2xl font-bold mb-4">Wybierz metodę płatności</h1>
            
            <div className="border-t border-gray-200 pt-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Cel darowizny:</span>
                <span className="font-semibold">{decodeURIComponent(goalName || '')}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Kwota:</span>
                <span className="text-2xl font-bold text-primary">{formatCurrency(amount)}</span>
              </div>
            </div>
          </div>

          {/* Payment Methods */}
          <div className="space-y-4">
            {paymentMethods.map((method) => (
              <button
                key={method.id}
                onClick={() => handleMethodSelect(method.id)}
                className={`w-full p-4 rounded-lg border-2 transition-all ${
                  selectedMethod === method.id
                    ? 'border-primary bg-primary/5'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="text-left">
                    <h3 className="font-semibold text-lg">{method.name}</h3>
                    <p className="text-sm text-gray-600">{method.description}</p>
                  </div>
                  
                  {selectedMethod === method.id && (
                    <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>

          {/* Pay Button */}
          <button
            onClick={handlePayment}
            disabled={!selectedMethod || loading}
            className="w-full btn-primary mt-8 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Przetwarzanie...' : `Zapłać ${formatCurrency(amount)}`}
          </button>

          {/* Security Notice */}
          <div className="mt-6 text-center text-sm text-gray-500">
            <p>🔒 Twoja płatność jest bezpieczna i szyfrowana</p>
          </div>
        </div>
      </div>
    </Layout>
  )
}