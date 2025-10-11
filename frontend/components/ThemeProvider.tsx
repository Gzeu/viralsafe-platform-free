'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

type Theme = 'light' | 'dark'

interface ThemeContextType {
  theme: Theme
  toggleTheme: () => void
  isDark: boolean
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

interface ThemeProviderProps {
  children: ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>('light')
  const [mounted, setMounted] = useState(false)

  // Load theme from localStorage on mount
  useEffect(() => {
    try {
      const savedTheme = localStorage.getItem('viralsafe-theme') as Theme
      if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
        setTheme(savedTheme)
      } else {
        // Check system preference
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        setTheme(systemDark ? 'dark' : 'light')
      }
    } catch (error) {
      // Fallback in case localStorage is not available
      console.warn('Could not access localStorage for theme:', error)
    }
    setMounted(true)
  }, [])

  // Apply theme to document
  useEffect(() => {
    if (mounted && typeof window !== 'undefined') {
      const root = document.documentElement
      root.classList.remove('light', 'dark')
      root.classList.add(theme)
      
      try {
        localStorage.setItem('viralsafe-theme', theme)
      } catch (error) {
        console.warn('Could not save theme to localStorage:', error)
      }
    }
  }, [theme, mounted])

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }

  const isDark = theme === 'dark'

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return (
      <div className="min-h-screen bg-white transition-colors duration-300">
        {children}
      </div>
    )
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, isDark }}>
      <div className={`${theme} transition-colors duration-300`}>
        {children}
      </div>
    </ThemeContext.Provider>
  )
}