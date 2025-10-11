import './globals.css'
import { ThemeProvider } from '../components/ThemeProvider'

export const metadata = {
  title: 'ViralSafe Platform v3.1 Enhanced',
  description: 'AI-Powered Content Safety Analysis with Dark Mode Support',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head />
      <body className="antialiased">
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}