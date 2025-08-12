import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { BuildingLibraryIcon, HeartIcon, FireIcon } from '@heroicons/react/24/outline'
import { apiCall } from '../utils/api'

export default function HomePage() {
  const [organization, setOrganization] = useState(null)
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [orgData, statsData] = await Promise.all([
        apiCall('/organization'),
        apiCall('/organization/stats')
      ])
      
      setOrganization(orgData)
      setStats(statsData)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getGoalIcon = (iconName) => {
    switch(iconName) {
      case 'church':
        return <BuildingLibraryIcon className="h-16 w-16 text-white" />
      case 'heart':
        return <HeartIcon className="h-16 w-16 text-white" />
      case 'candle':
        return <FireIcon className="h-16 w-16 text-white" />
      default:
        return <HeartIcon className="h-16 w-16 text-white" />
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
      minimumFractionDigits: 0
    }).format(amount)
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
      {/* Hero Section with Background */}
      <div 
        className="relative bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: `url('/bramkamvp/assets/mist_3.png')` }}
      >
        <div className="absolute inset-0 bg-gradient-to-b from-primary/80 to-secondary/90"></div>
        
        <div className="relative container mx-auto px-4 py-16 md:py-24">
          <div className="text-center text-white max-w-3xl mx-auto">
            <img 
              src="/bramkamvp/assets/mist_male_logo-DBJx8Hn_.png" 
              alt="Logo" 
              className="h-24 md:h-32 mx-auto mb-6"
            />
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              {organization?.name}
            </h1>
            <p className="text-xl md:text-2xl mb-8 opacity-90">
              {organization?.description}
            </p>
            
            <h2 className="text-2xl md:text-3xl font-semibold mb-8">
              Wybierz cel:
            </h2>
          </div>
        </div>
      </div>

      {/* Goals Section */}
      <div className="container mx-auto px-4 py-12 -mt-20 relative z-10">
        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {organization?.goals.map((goal) => (
            <Link
              key={goal.id}
              to={`/cel/${goal.id}`}
              className="card group hover:scale-105 transition-transform duration-200"
            >
              <div className="flex flex-col items-center text-center">
                <div className="bg-primary group-hover:bg-secondary rounded-full p-6 mb-4 transition-colors">
                  {getGoalIcon(goal.icon)}
                </div>
                
                <h3 className="text-xl font-semibold mb-2 text-gray-800">
                  {goal.name}
                </h3>
                
                <p className="text-gray-600 mb-4 text-sm">
                  {goal.description}
                </p>
                
                <div className="w-full">
                  <div className="flex justify-between text-sm text-gray-500 mb-2">
                    <span>Zebrano</span>
                    <span>Cel</span>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
                    <div 
                      className="bg-accent h-3 rounded-full transition-all duration-300"
                      style={{ width: `${Math.min((goal.collected_amount / goal.target_amount) * 100, 100)}%` }}
                    ></div>
                  </div>
                  
                  <div className="flex justify-between text-sm font-semibold">
                    <span className="text-accent">{formatCurrency(goal.collected_amount)}</span>
                    <span className="text-gray-700">{formatCurrency(goal.target_amount)}</span>
                  </div>
                </div>
                
                <button className="btn-primary mt-4 w-full">
                  Wesprzyj
                </button>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Stats Section */}
      {stats && (
        <div className="bg-gray-50 py-12">
          <div className="container mx-auto px-4">
            <div className="text-center max-w-2xl mx-auto">
              <h2 className="text-3xl font-bold mb-8 text-gray-800">
                Razem pomagamy
              </h2>
              
              <div className="grid grid-cols-2 gap-8">
                <div>
                  <p className="text-4xl font-bold text-primary">
                    {formatCurrency(stats.total_collected)}
                  </p>
                  <p className="text-gray-600 mt-2">Zebrane środki</p>
                </div>
                
                <div>
                  <p className="text-4xl font-bold text-accent">
                    {stats.progress_percentage}%
                  </p>
                  <p className="text-gray-600 mt-2">Realizacji celów</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}