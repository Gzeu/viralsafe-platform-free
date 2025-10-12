import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ViralSafe Platform - Free Tier',
  description: 'AI-powered content safety analysis with scam detection, phishing analysis & risk scoring',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ro" className="dark">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
          <header className="border-b border-gray-700">
            <div className="container mx-auto px-4 py-4">
              <h1 className="text-2xl font-bold text-white">🛡️ ViralSafe Platform</h1>
              <p className="text-gray-300">Analiză de siguranță conținut cu AI</p>
            </div>
          </header>
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}