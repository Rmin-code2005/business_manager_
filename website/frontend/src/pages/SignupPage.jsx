import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../api/auth'
import { useAuth } from '../context/AuthContext'
import Input from '../components/Input'
import Button from '../components/Button'
import styles from './AuthPage.module.css'

async function registerUser(data) {
  const res = await fetch('/api/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  const json = await res.json()
  if (!res.ok) {
    // DRF returns { field: ['error msg'] } or { detail: '...' }
    const msg = json.detail
      || Object.entries(json).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join(' | ')
    throw new Error(msg)
  }
  return json
}

export default function SignupPage() {
  const navigate = useNavigate()
  const { onLogin } = useAuth()

  const [form, setForm] = useState({
    email: '', password: '', confirmPassword: '',
    first_name: '', last_name: '', phone: '', gender: '',
  })
  const [errors, setErrors]   = useState({})
  const [apiError, setApiError] = useState('')
  const [loading, setLoading] = useState(false)

  function handleChange(e) {
    const { name, value } = e.target
    setForm(f => ({ ...f, [name]: value }))
    if (errors[name]) setErrors(e => ({ ...e, [name]: '' }))
    if (apiError) setApiError('')
  }

  function validate() {
    const errs = {}
    if (!form.first_name.trim()) errs.first_name = 'First name is required'
    if (!form.last_name.trim())  errs.last_name  = 'Last name is required'
    if (!form.email)             errs.email      = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(form.email)) errs.email = 'Enter a valid email'
    if (!form.phone)             errs.phone      = 'Phone is required'
    else if (form.phone.length > 11) errs.phone  = 'Max 11 digits'
    if (!form.password)          errs.password   = 'Password is required'
    else if (form.password.length < 8) errs.password = 'At least 8 characters'
    if (form.password !== form.confirmPassword) errs.confirmPassword = 'Passwords do not match'
    return errs
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }

    setLoading(true)
    try {
      const { confirmPassword, ...payload } = form
      await registerUser(payload)

      // Auto-login after successful registration
      const loginData = await login(form.email, form.password)
      onLogin(loginData)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setApiError(err.message || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      {/* Left decorative panel */}
      <div className={styles.panel}>
        <div className={styles.panelInner}>
          <div className={styles.logo}>BM</div>
          <h1 className={styles.panelTitle}>Bissinus Manager</h1>
          <p className={styles.panelSub}>
            Start managing your<br />business smarter today.
          </p>
          <div className={styles.dots}>
            <span /><span /><span />
          </div>
        </div>
      </div>

      {/* Form side */}
      <div className={styles.formSide}>
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h2 className={styles.cardTitle}>Create account</h2>
            <p className={styles.cardSub}>Fill in your details to get started</p>
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
            <div className={styles.row}>
              <Input
                id="first_name"
                name="first_name"
                type="text"
                label="First name"
                placeholder="Armin"
                value={form.first_name}
                onChange={handleChange}
                error={errors.first_name}
                autoFocus
              />
              <Input
                id="last_name"
                name="last_name"
                type="text"
                label="Last name"
                placeholder="Doe"
                value={form.last_name}
                onChange={handleChange}
                error={errors.last_name}
              />
            </div>

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
            />

            <div className={styles.row}>
              <Input
                id="phone"
                name="phone"
                type="tel"
                label="Phone number"
                placeholder="09123456789"
                value={form.phone}
                onChange={handleChange}
                error={errors.phone}
              />

              {/* Gender select */}
              <div className={styles.selectWrapper}>
                <label htmlFor="gender" className={styles.selectLabel}>
                  Gender <span className={styles.optional}>(optional)</span>
                </label>
                <select
                  id="gender"
                  name="gender"
                  className={styles.select}
                  value={form.gender}
                  onChange={handleChange}
                >
                  <option value="">Select…</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <Input
              id="password"
              name="password"
              type="password"
              label="Password"
              placeholder="Min. 8 characters"
              value={form.password}
              onChange={handleChange}
              error={errors.password}
              autoComplete="new-password"
            />
            <Input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              label="Confirm password"
              placeholder="Repeat your password"
              value={form.confirmPassword}
              onChange={handleChange}
              error={errors.confirmPassword}
              autoComplete="new-password"
            />

            <Button type="submit" loading={loading}>
              Create account
            </Button>
          </form>

          <p className={styles.switchLink}>
            Already have an account?{' '}
            <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
