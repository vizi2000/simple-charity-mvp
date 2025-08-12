import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { ArrowLeftIcon, QrCodeIcon } from '@heroicons/react/24/outline'
import { BuildingLibraryIcon, HeartIcon, FireIcon } from '@heroicons/react/24/outline'
import { apiCall } from '../utils/api'

export default function GoalPage() {
  const { goalId } = useParams()
  const navigate = useNavigate()
  const [goal, setGoal] = useState(null)
  const [organization, setOrganization] = useState(null)
  const [amount, setAmount] = useState('')
  const [customAmount, setCustomAmount] = useState(false)
  const [donorName, setDonorName] = useState('')
  const [donorEmail, setDonorEmail] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [showQR, setShowQR] = useState(false)

  const predefinedAmounts = [20, 50, 100, 200, 500]

  useEffect(() => {
    loadGoalData()
  }, [goalId])

  const loadGoalData = async () => {
    try {
      const [goalData, orgData] = await Promise.all([
        apiCall(`/organization/goal/${goalId}`),
        apiCall('/organization')
      ])
      
      setGoal(goalData)
      setOrganization(orgData)
    } catch (error) {
      console.error('Error loading goal:', error)
      navigate('/')
    } finally {
      setLoading(false)
    }
  }

  const getGoalIcon = (iconName) => {
    switch(iconName) {
      case 'church':
        return <BuildingLibraryIcon className="h-24 w-24 text-white" />
      case 'heart':
        return <HeartIcon className="h-24 w-24 text-white" />
      case 'candle':
        return <FireIcon className="h-24 w-24 text-white" />
      default:
        return <HeartIcon className="h-24 w-24 text-white" />
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const handleAmountSelect = (value) => {
    setAmount(value)
    setCustomAmount(false)
  }

  const handleCustomAmount = () => {
    setCustomAmount(true)
    setAmount('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    console.log('Form submitted!', { amount, goalId }) // Debug log
    
    const finalAmount = parseFloat(amount)
    if (!finalAmount || finalAmount <= 0) {
      alert('Proszę podać prawidłową kwotę')
      return
    }

    setSubmitting(true)

    try {
      const response = await fetch(`${window.location.origin}/bramkamvp/api/payments/initiate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          goal_id: goalId,
          organization_id: organization?.id || 'misjonarze',
          amount: finalAmount,
          donor_name: donorName || null,
          donor_email: donorEmail || null,
          message: message || null,
          is_anonymous: false
        })
      })

      if (!response.ok) {
        throw new Error('Failed to initiate payment')
      }

      const data = await response.json()
      console.log('Payment response:', data) // Debug log
      
      // Handle Fiserv form submission
      if (data.form_url && data.form_data) {
        console.log('Creating form for Fiserv submission') // Debug log
        
        // Create and submit form dynamically
        const form = document.createElement('form')
        form.method = 'POST'
        form.action = data.form_url
        
        // Add all form fields from backend
        Object.entries(data.form_data).forEach(([key, value]) => {
          const input = document.createElement('input')
          input.type = 'hidden'
          input.name = key
          input.value = value
          form.appendChild(input)
        })
        
        document.body.appendChild(form)
        form.submit()
      } else if (data.payment_url) {
        // Fallback for old payment_url format
        console.log('Redirecting to:', data.payment_url) // Debug log
        window.location.href = data.payment_url
      } else {
        throw new Error('No payment form data received')
      }
    } catch (error) {
      console.error('Payment error:', error)
      alert('Wystąpił błąd podczas inicjowania płatności. Proszę spróbować ponownie.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-gray-600">Ładowanie...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      {/* Hero Section */}
      <div className="bg-gradient-to-b from-primary to-secondary text-white py-12">
        <div className="container mx-auto px-4">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-white/80 hover:text-white mb-6 transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5" />
            <span>Powrót</span>
          </button>
          
          <div className="text-center max-w-3xl mx-auto">
            <div className="bg-white/10 rounded-full p-8 inline-block mb-6">
              {getGoalIcon(goal?.icon)}
            </div>
            
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              {goal?.name}
            </h1>
            
            <p className="text-xl opacity-90 mb-8">
              {goal?.description}
            </p>
            
            <div className="bg-white/10 rounded-lg p-6 max-w-md mx-auto">
              <div className="flex justify-between text-sm mb-2">
                <span>Zebrano</span>
                <span>Cel</span>
              </div>
              
              <div className="w-full bg-white/20 rounded-full h-4 mb-3">
                <div 
                  className="bg-accent h-4 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min((goal?.collected_amount / goal?.target_amount) * 100, 100)}%` }}
                ></div>
              </div>
              
              <div className="flex justify-between font-semibold">
                <span>{formatCurrency(goal?.collected_amount)}</span>
                <span>{formatCurrency(goal?.target_amount)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Donation Form */}
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          <div className="card">
            <h2 className="text-2xl font-bold mb-6 text-center">
              Złóż ofiarę
            </h2>
            
            <form onSubmit={handleSubmit}>
              {/* Amount Selection */}
              <div className="mb-8">
                <label className="block text-sm font-medium text-gray-700 mb-4">
                  Wybierz kwotę
                </label>
                
                <div className="grid grid-cols-3 md:grid-cols-5 gap-3 mb-4">
                  {predefinedAmounts.map((value) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() => handleAmountSelect(value)}
                      className={`py-3 px-4 rounded-lg font-semibold transition-colors ${
                        amount == value && !customAmount
                          ? 'bg-primary text-white'
                          : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                      }`}
                    >
                      {value} zł
                    </button>
                  ))}
                </div>
                
                <button
                  type="button"
                  onClick={handleCustomAmount}
                  className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
                    customAmount
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                  }`}
                >
                  Inna kwota
                </button>
                
                {customAmount && (
                  <div className="mt-4">
                    <input
                      type="number"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      placeholder="Wpisz kwotę"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                      min="1"
                      step="0.01"
                      required
                    />
                  </div>
                )}
              </div>

              {/* Donor Information (Optional) */}
              <div className="mb-8 space-y-4">
                <h3 className="text-lg font-semibold mb-4">
                  Dane darczyńcy (opcjonalne)
                </h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Imię i nazwisko
                  </label>
                  <input
                    type="text"
                    value={donorName}
                    onChange={(e) => setDonorName(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    placeholder="Jan Kowalski"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    value={donorEmail}
                    onChange={(e) => setDonorEmail(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    placeholder="jan@example.com"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Wiadomość
                  </label>
                  <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    placeholder="Wpisz swoją intencję lub wiadomość..."
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={!amount || submitting}
                className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? 'Przetwarzanie...' : 'Przejdź do płatności'}
              </button>
            </form>
          </div>

          {/* QR Code Section */}
          <div className="card mt-8 text-center">
            <button
              onClick={() => setShowQR(!showQR)}
              className="flex items-center gap-2 mx-auto text-primary hover:text-secondary transition-colors"
            >
              <QrCodeIcon className="h-6 w-6" />
              <span className="font-semibold">
                {showQR ? 'Ukryj kod QR' : 'Pokaż kod QR'}
              </span>
            </button>
            
            {showQR && (
              <div className="mt-6">
                <p className="text-sm text-gray-600 mb-4">
                  Zeskanuj kod QR, aby szybko przejść do tej strony
                </p>
                <img
                  src={`/api/organization/qr/${goalId}`}
                  alt="QR Code"
                  className="mx-auto"
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}