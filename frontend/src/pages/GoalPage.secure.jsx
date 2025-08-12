import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'

export default function GoalPage() {
  const { goalId } = useParams()
  const navigate = useNavigate()
  const formRef = useRef(null)
  const [goal, setGoal] = useState(null)
  const [organization, setOrganization] = useState(null)
  const [amount, setAmount] = useState('')
  const [donorName, setDonorName] = useState('')
  const [donorEmail, setDonorEmail] = useState('')
  const [message, setMessage] = useState('')
  const [isAnonymous, setIsAnonymous] = useState(false)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [paymentFormData, setPaymentFormData] = useState(null)

  const predefinedAmounts = [10, 25, 50, 100, 200, 500]

  // API URL configuration
  const getApiUrl = (path) => {
    if (window.location.hostname === 'borgtools.ddns.net') {
      return `https://borgtools.ddns.net/bramkamvp/api${path}`;
    }
    return `/api${path}`;
  };

  useEffect(() => {
    loadData()
  }, [goalId])

  useEffect(() => {
    // Auto-submit form when payment data is ready
    if (paymentFormData && formRef.current) {
      console.log('Submitting payment form to Fiserv...')
      formRef.current.submit()
    }
  }, [paymentFormData])

  const loadData = async () => {
    try {
      const [goalResponse, orgResponse] = await Promise.all([
        fetch(getApiUrl(`/organization/goal/${goalId}`)),
        fetch(getApiUrl('/organization'))
      ])
      
      const goalData = await goalResponse.json()
      const orgData = await orgResponse.json()
      
      setGoal(goalData)
      setOrganization(orgData)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!amount || parseFloat(amount) <= 0) {
      alert('Proszę podać prawidłową kwotę')
      return
    }

    setSubmitting(true)
    
    try {
      // SECURITY: Send data to backend, which will generate hash
      // Never generate hash in frontend!
      const response = await fetch(getApiUrl('/payments/initiate'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          goal_id: goalId,
          amount: parseFloat(amount),
          donor_name: isAnonymous ? 'Anonimowy' : donorName,
          donor_email: donorEmail,
          message: message,
          is_anonymous: isAnonymous
        })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Payment initiated:', data)
        
        // Set form data for auto-submit
        setPaymentFormData({
          url: data.form_url,
          fields: data.form_data
        })
        
        // Note: Form will auto-submit via useEffect
      } else {
        const error = await response.json()
        console.error('Payment initiation failed:', error)
        alert('Wystąpił błąd podczas inicjowania płatności')
        setSubmitting(false)
      }
    } catch (error) {
      console.error('Error initiating payment:', error)
      alert('Wystąpił błąd podczas inicjowania płatności')
      setSubmitting(false)
    }
  }

  const getProgressPercentage = () => {
    if (!goal) return 0
    return Math.min(100, (goal.collected_amount / goal.target_amount) * 100)
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="animate-pulse text-gray-500">Ładowanie...</div>
        </div>
      </Layout>
    )
  }

  if (!goal || !organization) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-gray-500">Nie znaleziono celu</div>
        </div>
      </Layout>
    )
  }

  // Show processing screen while redirecting to Fiserv
  if (paymentFormData) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-lg font-semibold mb-2">Przekierowanie do bramki płatności...</p>
            <p className="text-gray-600">Za chwilę zostaniesz przekierowany do bezpiecznej strony płatności.</p>
            
            {/* Hidden form that auto-submits to Fiserv */}
            <form 
              ref={formRef}
              method="POST" 
              action={paymentFormData.url}
              style={{ display: 'none' }}
            >
              {Object.entries(paymentFormData.fields).map(([key, value]) => (
                <input 
                  key={key}
                  type="hidden" 
                  name={key} 
                  value={value}
                />
              ))}
            </form>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <button
          onClick={() => navigate('/')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeftIcon className="w-5 h-5 mr-2" />
          Powrót
        </button>

        <div className="bg-white rounded-xl shadow-sm p-8">
          {/* Goal Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">{goal.name}</h1>
            <p className="text-lg text-gray-600">{goal.description}</p>
          </div>

          {/* Progress Section */}
          <div className="mb-8 p-6 bg-gray-50 rounded-lg">
            <div className="mb-4">
              <div className="flex justify-between text-lg font-semibold mb-2">
                <span>Zebrano</span>
                <span style={{ color: organization.primary_color }}>
                  {goal.collected_amount?.toLocaleString('pl-PL')} zł
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="h-3 rounded-full transition-all duration-500"
                  style={{ 
                    width: `${getProgressPercentage()}%`,
                    backgroundColor: organization.primary_color 
                  }}
                />
              </div>
              <div className="flex justify-between text-sm text-gray-500 mt-2">
                <span>{Math.round(getProgressPercentage())}% celu</span>
                <span>Cel: {goal.target_amount?.toLocaleString('pl-PL')} zł</span>
              </div>
            </div>
          </div>

          {/* Donation Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Amount Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Wybierz kwotę wsparcia
              </label>
              <div className="grid grid-cols-3 gap-3 mb-4">
                {predefinedAmounts.map((presetAmount) => (
                  <button
                    key={presetAmount}
                    type="button"
                    onClick={() => setAmount(presetAmount.toString())}
                    className={`py-3 px-4 rounded-lg border-2 font-medium transition-colors ${
                      amount === presetAmount.toString()
                        ? 'border-blue-500 bg-blue-50 text-blue-600'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    {presetAmount} zł
                  </button>
                ))}
              </div>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Inna kwota"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                step="0.01"
                min="1"
                max="100000"
                required
              />
            </div>

            {/* Anonymous Donation */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="anonymous"
                checked={isAnonymous}
                onChange={(e) => setIsAnonymous(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="anonymous" className="ml-2 text-sm text-gray-700">
                Wpłata anonimowa
              </label>
            </div>

            {/* Donor Information */}
            {!isAnonymous && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Imię i nazwisko
                  </label>
                  <input
                    type="text"
                    value={donorName}
                    onChange={(e) => setDonorName(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required={!isAnonymous}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email (opcjonalnie)
                  </label>
                  <input
                    type="email"
                    value={donorEmail}
                    onChange={(e) => setDonorEmail(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Dla potwierdzenia płatności"
                  />
                </div>
              </>
            )}

            {/* Message */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Wiadomość (opcjonalnie)
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Możesz dodać wiadomość dla organizacji..."
              />
            </div>

            {/* Security Note */}
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                🔒 <strong>Bezpieczna płatność</strong>
              </p>
              <p className="text-sm text-blue-700 mt-1">
                • Twoje dane są szyfrowane i bezpieczne<br/>
                • Płatność jest procesowana przez certyfikowany system Fiserv/Polcard<br/>
                • Nie przechowujemy danych Twojej karty płatniczej
              </p>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submitting}
              className="w-full py-4 px-6 rounded-lg text-white font-medium text-lg hover:opacity-90 transition-opacity disabled:opacity-50"
              style={{ backgroundColor: organization.primary_color }}
            >
              {submitting ? 'Przetwarzanie...' : `Wpłać ${amount || '...'} zł`}
            </button>
          </form>

          {/* Additional Info */}
          <div className="mt-6 text-center text-sm text-gray-500">
            <p>Akceptujemy płatności kartą, BLIK, Apple Pay i Google Pay</p>
          </div>
        </div>
      </div>
    </Layout>
  )
}