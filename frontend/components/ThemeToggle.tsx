'use client'

import { useTheme } from './ThemeProvider'
import { Moon, Sun } from 'lucide-react'

export function ThemeToggle() {
  const { isDark, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className="
        relative p-2 rounded-lg transition-all duration-300 ease-in-out
        bg-gray-100 hover:bg-gray-200 
        dark:bg-gray-800 dark:hover:bg-gray-700
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
        dark:focus:ring-offset-gray-900
        group
      "
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      <div className="relative w-5 h-5">
        {/* Sun Icon */}
        <Sun 
          className={`
            absolute inset-0 w-5 h-5 text-yellow-500 transition-all duration-300
            ${isDark ? 'opacity-0 rotate-90 scale-75' : 'opacity-100 rotate-0 scale-100'}
          `}
        />
        
        {/* Moon Icon */}
        <Moon 
          className={`
            absolute inset-0 w-5 h-5 text-blue-400 transition-all duration-300
            ${isDark ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 -rotate-90 scale-75'}
          `}
        />
      </div>
      
      {/* Tooltip */}
      <span className="
        absolute -bottom-8 left-1/2 transform -translate-x-1/2 
        px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 
        group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap
        dark:bg-gray-100 dark:text-gray-900 pointer-events-none z-50
      ">
        {isDark ? 'Light Mode' : 'Dark Mode'}
      </span>
    </button>
  )
}