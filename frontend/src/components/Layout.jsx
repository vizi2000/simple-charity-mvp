import React from 'react'
import { PhoneIcon, MapPinIcon } from '@heroicons/react/24/outline'

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-1">
        {children}
      </main>
      
      <footer className="bg-secondary text-white py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <img src="/src/assets/mist_male_logo.png" alt="Logo" className="h-12 mb-2" />
              <p className="text-sm">Misjonarze świętego Wincentego a Paulo</p>
            </div>
            
            <div className="flex flex-col md:flex-row gap-6 text-sm">
              <div className="flex items-center gap-2">
                <MapPinIcon className="h-4 w-4" />
                <span>OBIEKT MONITOROWANY</span>
              </div>
              <div className="flex items-center gap-2">
                <PhoneIcon className="h-4 w-4" />
                <span>tel. 790 525 400</span>
              </div>
            </div>
          </div>
          
          <div className="mt-6 pt-6 border-t border-primary/20 text-center text-xs">
            <p>© 2025 Misjonarze Parafia Świętej Rodziny. Wszelkie prawa zastrzeżone.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}