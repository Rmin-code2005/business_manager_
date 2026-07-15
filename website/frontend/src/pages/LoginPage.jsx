import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../api/auth'
import { useAuth } from '../context/AuthContext'
import Input from '../components/Input'
import Button from '../components/Button'
import styles from './AuthPage.module.css'

export default function LoginPage() {
  const navigate = useNavigate()
  const { onLogin } = useAuth()

  const [form, setForm]       = useState({ email: '', password: '' })
  const [errors, setErrors]   = useState({})
  const [apiError, setApiError] = useState('')
  const [loading, setLoading] = useState(false)

  function handleChange(e) {
    const { name, value } = e.target
    setForm(f => ({ ...f, [name]: value }))
    // Clear field error on change
    if (errors[name]) setErrors(e => ({ ...e, [name]: '' }))
    if (apiError) setApiError('')
  }

  function validate() {
    const errs = {}
    if (!form.email)    errs.email    = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(form.email)) errs.email = 'Enter a valid email'
    if (!form.password) errs.password = 'Password is required'
    return errs
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }

    setLoading(true)
    try {
      const data = await login(form.email, form.password)
      onLogin(data)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setApiError(err.message || 'Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      {/* Left panel — decorative */}
      <div className={styles.panel}>
        <div className={styles.panelInner}>
          <div className={styles.logo}>BM</div>
          <h1 className={styles.panelTitle}>Bissinus Manager</h1>
          <p className={styles.panelSub}>
            Your business, organised.<br />One dashboard to run it all.
          </p>
          <div className={styles.dots}>
            <span /><span /><span />
          </div>
        </div>
      </div>

      {/* Right panel — form */}
      <div className={styles.formSide}>
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h2 className={styles.cardTitle}>Welcome back</h2>
            <p className={styles.cardSub}>Sign in to your account</p>
          </div>

          {apiError && (
            <div className={styles.alert}>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M8 5v3.5M8 10.5v.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
              {apiError}
            </div>
          )}

          <form onSubmit={handleSubmit} className={styles.form} noValidate>
            <Input
              id="email"
              name="email"
              type="email"
              label="Email address"
              placeholder="you@example.com"
              value={form.email}
              onChange={handleChange}
              error={errors.email}
              autoComplete="email"
              autoFocus
            />
            <Input
              id="password"
              name="password"
              type="password"
              label="Password"
              placeholder="••••••••"
              value={form.password}
              onChange={handleChange}
              error={errors.password}
              autoComplete="current-password"
            />
            <Button type="submit" loading={loading}>
              Sign in
            </Button>
          </form>

          <p className={styles.switchLink}>
            Don't have an account?{' '}
            <Link to="/signup">Create one</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
