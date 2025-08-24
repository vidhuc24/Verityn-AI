import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/ThemeProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Verityn AI - Audit Intelligence Platform',
  description: 'AI-powered document analysis and compliance insights for audit, risk & compliance professionals',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning className="dark">
      <body className={inter.className}>
        <ThemeProvider
          defaultTheme="dark"
          storageKey="verityn-ui-theme"
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
} 