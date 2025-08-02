import { useState, useEffect, useContext } from 'react'
import { ThemeProviderContext } from '@/components/theme-provider'

export const useTheme = (storageKey = 'vite-ui-theme', defaultTheme = 'system') => {
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>(
    () => (localStorage.getItem(storageKey) as 'light' | 'dark' | 'system') || defaultTheme
  )

  useEffect(() => {
    const root = window.document.documentElement
    root.classList.remove('light', 'dark')
    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      root.classList.add(systemTheme)
      return
    }
    root.classList.add(theme)
  }, [theme])

  return [theme, setTheme] as const
}

export const useThemeContext = () => {
    const context = useContext(ThemeProviderContext)
    if (context === undefined) {
        throw new Error("useThemeContext must be used within a ThemeProvider")
    }
    return context
}
