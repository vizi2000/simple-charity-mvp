import React, { useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import Layout from '../components/Layout'
import { CheckCircleIcon } from '@heroicons/react/24/solid'

export default function ThankYouPage() {
  const [searchParams] = useSearchParams()
  const amount = searchParams.get('amount')
  const goal = searchParams.get('goal')
  const paymentMethod = searchParams.get('method')

  useEffect(() => {
    // Scroll to top on mount
    window.scrollTo(0, 0)
  }, [])

  const formatCurrency = (value) => {
    if (!value) return ''
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
      minimumFractionDigits: 0
    }).format(parseFloat(value))
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
        return null
    }
  }

  return (
    <Layout>
      {/* Thank You Section with Background */}
      <div 
        className="relative min-h-screen flex items-center justify-center bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: `url('/src/assets/Mis - Tarnów  - ekran podziękowania - granat.jpg')` }}
      >
        <div className="absolute inset-0 bg-gradient-to-b from-primary/70 to-secondary/80"></div>
        
        <div className="relative container mx-auto px-4 py-16 text-center text-white">
          <div className="max-w-2xl mx-auto">
            {/* Success Icon */}
            <div className="mb-8">
              <CheckCircleIcon className="h-32 w-32 mx-auto text-green-400 animate-pulse" />
            </div>

            {/* Main Message */}
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Dziękujemy za złożoną ofiarę!
            </h1>
            
            <p className="text-xl md:text-2xl mb-4 opacity-90">
              Misjonarze świętego Wincentego a Paulo
            </p>

            {/* Donation Details */}
            {amount && (
              <div className="bg-white/10 rounded-lg p-6 mb-8 max-w-md mx-auto">
                <p className="text-lg mb-2">Twoja darowizna</p>
                <p className="text-3xl font-bold mb-2">{formatCurrency(amount)}</p>
                {goal && (
                  <p className="text-lg opacity-90">na cel: {decodeURIComponent(goal)}</p>
                )}
                {paymentMethod && getPaymentMethodName() && (
                  <p className="text-md opacity-80 mt-2">Metoda płatności: {getPaymentMethodName()}</p>
                )}
              </div>
            )}

            {/* Thank You Message */}
            <div className="mb-12">
              <p className="text-lg md:text-xl leading-relaxed opacity-90">
                Twoje wsparcie pomaga nam kontynuować naszą misję
                i nieść pomoc potrzebującym. Niech Bóg Ci błogosławi
                za Twoją hojność i dobre serce.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/" className="btn-secondary">
                Powrót do strony głównej
              </Link>
              <Link to="/" className="btn-primary">
                Złóż kolejną ofiarę
              </Link>
            </div>

            {/* Footer Info */}
            <div className="mt-16 text-sm opacity-70">
              <p>Parafia Świętej Rodziny w Tarnowie</p>
              <p>tel. 790 525 400</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}