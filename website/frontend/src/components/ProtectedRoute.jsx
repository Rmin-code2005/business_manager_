import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/**
 * Wraps a route: redirects to /login if not authenticated.
 * Shows nothing while the session check is still loading.
 */
export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--text-secondary)',
        fontFamily: 'var(--font-body)',
      }}>
        <span style={{ fontSize: 14, letterSpacing: '0.05em' }}>Loading…</span>
      </div>
    )
  }

  return user ? children : <Navigate to="/login" replace />
}
