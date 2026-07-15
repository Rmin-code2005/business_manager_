import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { getMe, logout as apiLogout, token } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)   // UserDetail object
  const [loading, setLoading] = useState(true)   // true while checking session

  // On mount: if we have a stored token, fetch user profile
  useEffect(() => {
    const accessToken = token.getAccess()
    if (!accessToken) {
      setLoading(false)
      return
    }
    getMe()
      .then(setUser)
      .catch(() => {
        token.clear()
      })
      .finally(() => setLoading(false))
  }, [])

  // Called after a successful login — receives the full login response
  const onLogin = useCallback((data) => {
    // data = { access, refresh, user: { id, email, first_name } }
    // Fetch full profile immediately
    getMe()
      .then(setUser)
      .catch(() => setUser(data.user))   // fallback to partial user from login
  }, [])

  const onLogout = useCallback(() => {
    apiLogout()
    setUser(null)
  }, [])

  // Re-fetch the user profile from /api/me/ — useful after editing profile fields
  const refreshUser = useCallback(() => {
    return getMe().then(setUser)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, onLogin, onLogout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
