import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { BuildingLibraryIcon, HeartIcon, FireIcon } from '@heroicons/react/24/outline'

export default function HomePage() {
  const [organization, setOrganization] = useState(null)
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  // Simple API URL detection
  const getApiUrl = (path) => {
    if (window.location.hostname === 'borgtools.ddns.net') {
      return `https://borgtools.ddns.net/bramkamvp/api${path}`;
    }
    return `/api${path}`;
  };

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [orgResponse, statsResponse] = await Promise.all([
        fetch(getApiUrl('/organization')),
        fetch(getApiUrl('/organization/stats'))
      ])
      
      const orgData = await orgResponse.json()
      const statsData = await statsResponse.json()
      
      setOrganization(orgData)
      setStats(statsData)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getGoalIcon = (goalId) => {
    switch(goalId) {
      case 'church':
        return <BuildingLibraryIcon className="w-8 h-8" />
      case 'poor':
        return <HeartIcon className="w-8 h-8" />
      case 'candles':
        return <FireIcon className="w-8 h-8" />
      default:
        return <HeartIcon className="w-8 h-8" />
    }
  }

  const getProgressPercentage = (collected, target) => {
    return Math.min(100, (collected / target) * 100)
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

  if (!organization) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-gray-500">Nie udało się załadować danych</div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="text-center mb-12">
          <img 
            src={organization.logo_url} 
            alt={organization.name}
            className="h-24 w-auto mx-auto mb-6"
          />
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            {organization.name}
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {organization.description}
          </p>
          <p className="text-lg text-gray-500 mt-2">
            {organization.location}
          </p>
        </div>

        {/* Stats Section */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div className="bg-white rounded-xl shadow-sm p-6 text-center">
              <div className="text-3xl font-bold text-blue-600">
                {stats.total_collected?.toLocaleString('pl-PL')} zł
              </div>
              <div className="text-gray-600 mt-2">Zebrane środki</div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6 text-center">
              <div className="text-3xl font-bold text-green-600">
                {stats.total_donors}
              </div>
              <div className="text-gray-600 mt-2">Darczyńców</div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6 text-center">
              <div className="text-3xl font-bold text-purple-600">
                {stats.total_payments}
              </div>
              <div className="text-gray-600 mt-2">Wpłat</div>
            </div>
          </div>
        )}

        {/* Goals Section */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Cele charytatywne</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {organization.goals?.map((goal) => (
              <Link
                key={goal.id}
                to={`/cel/${goal.id}`}
                className="block bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6"
              >
                <div className="flex items-center mb-4" style={{ color: organization.primary_color }}>
                  {getGoalIcon(goal.id)}
                  <h3 className="text-xl font-semibold ml-3">{goal.name}</h3>
                </div>
                <p className="text-gray-600 mb-4">{goal.description}</p>
                
                {/* Progress Bar */}
                <div className="mb-2">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Zebrano</span>
                    <span>{goal.collected_amount?.toLocaleString('pl-PL')} zł</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="h-2 rounded-full transition-all duration-500"
                      style={{ 
                        width: `${getProgressPercentage(goal.collected_amount, goal.target_amount)}%`,
                        backgroundColor: organization.primary_color 
                      }}
                    />
                  </div>
                  <div className="flex justify-between text-sm text-gray-500 mt-1">
                    <span>{Math.round(getProgressPercentage(goal.collected_amount, goal.target_amount))}%</span>
                    <span>Cel: {goal.target_amount?.toLocaleString('pl-PL')} zł</span>
                  </div>
                </div>

                <button 
                  className="w-full mt-4 py-2 px-4 rounded-lg text-white font-medium hover:opacity-90 transition-opacity"
                  style={{ backgroundColor: organization.primary_color }}
                >
                  Wesprzyj
                </button>
              </Link>
            ))}
          </div>
        </div>

        {/* Contact Section */}
        <div className="bg-white rounded-xl shadow-sm p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Kontakt</h2>
          <div className="space-y-2 text-gray-600">
            <p>Telefon: {organization.contact_phone}</p>
            <p>Email: {organization.contact_email}</p>
            {organization.website && (
              <p>
                Strona: <a href={organization.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                  {organization.website}
                </a>
              </p>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}