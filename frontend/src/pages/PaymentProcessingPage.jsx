import React, { useEffect } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import Layout from '../components/Layout'
import { ArrowPathIcon } from '@heroicons/react/24/outline'

export default function PaymentProcessingPage() {
  const { paymentId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const { amount, goalName, goalId, paymentMethod } = location.state || {}

  useEffect(() => {
    processPayment()
  }, [])

  const processPayment = async () => {
    try {
      // Simulate initial processing time
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Get payment form data for Fiserv IPG
      const formDataResponse = await fetch(`/api/payments/${paymentId}/form-data`)
      
      if (formDataResponse.ok) {
        const formData = await formDataResponse.json()
        
        // Create and submit form to Fiserv gateway
        const form = document.createElement('form')
        form.method = 'POST'
        form.action = formData.form_action
        
        // Add all form fields
        Object.entries(formData.form_fields).forEach(([key, value]) => {
          const input = document.createElement('input')
          input.type = 'hidden'
          input.name = key
          input.value = value
          form.appendChild(input)
        })
        
        // Append form to body and submit
        document.body.appendChild(form)
        form.submit()
        return
      }
      
      // Fallback to mock payment processing for development
      const response = await fetch(`/api/payments/${paymentId}/process-mock`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          payment_method: paymentMethod
        })
      })

      if (response.ok) {
        // Redirect to thank you page with payment details
        navigate(`/dziekujemy?amount=${amount}&goal=${encodeURIComponent(goalName || '')}&method=${paymentMethod}`)
      } else {
        throw new Error('Payment processing failed')
      }
    } catch (error) {
      console.error('Payment error:', error)
      // In case of error, still redirect to thank you page (for demo purposes)
      navigate(`/dziekujemy?amount=${amount}&goal=${encodeURIComponent(goalName || '')}&method=${paymentMethod}`)
    }
  }

  const getPaymentMethodName = () => {
    switch(paymentMethod) {
      case 'apple-pay':
        return 'Apple Pay'
      case 'google-pay':
        return 'Google Pay'
      case 'blik':
        return 'BLIK'
      case 'bank-transfer':
        return 'Przelew bankowy'
      case 'card':
        return 'Karta płatnicza'
      default:
        return 'Płatność'
    }
  }

  return (
    <Layout>
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          {/* Processing Animation */}
          <div className="mb-8">
            <ArrowPathIcon className="h-20 w-20 mx-auto text-primary animate-spin" />
          </div>

          {/* Processing Message */}
          <h2 className="text-2xl font-bold mb-4">Przetwarzanie płatności...</h2>
          
          <div className="space-y-2 text-gray-600">
            <p>Łączenie z {getPaymentMethodName()}</p>
            <p className="text-sm">To może potrwać kilka sekund</p>
          </div>

          {/* Progress Bar */}
          <div className="mt-8 w-64 mx-auto">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-primary h-2 rounded-full animate-pulse" style={{ width: '75%' }}></div>
            </div>
          </div>

          {/* Security Notice */}
          <div className="mt-8 text-sm text-gray-500">
            <p>🔒 Bezpieczne połączenie</p>
          </div>
        </div>
      </div>
    </Layout>
  )
}