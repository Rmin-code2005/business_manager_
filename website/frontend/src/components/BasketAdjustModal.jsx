import { useState } from 'react'
import { increaseBasketRaw, decreaseBasketRaw } from '../api/auth'
import styles from './BasketAdjustModal.module.css'

function IconClose() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
      <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  )
}

/**
 * Props:
 *   type           string    'crypto' | 'currency' | 'gold'   (display only)
 *   apiTypeCode    string    'cr' | 'ca' | 'g'                 (sent to backend, exact)
 *   color          string    'blue' | 'green' | 'yellow'
 *   label          string    e.g. "Currency"
 *   initialSymbol  string?   pre-fill symbol (when adjusting an existing basket)
 *   onClose        fn
 *   onSuccess      fn        called after a successful create/adjust, to refresh lists
 */
export default function BasketAdjustModal({ type, apiTypeCode, color, label, initialSymbol = '', onClose, onSuccess }) {
  const [symbol, setSymbol]     = useState(initialSymbol)
  const [value, setValue]       = useState('')
  const [mode, setMode]         = useState('increase') // 'increase' | 'decrease'
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')
  const [success, setSuccess]   = useState(false)

  const isEditingExisting = Boolean(initialSymbol)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    const cleanSymbol = symbol.trim().toUpperCase()
    if (!cleanSymbol) { setError('Symbol is required'); return }
    if (!value || isNaN(Number(value)) || Number(value) <= 0) {
      setError('Enter a valid positive amount')
      return
    }
    if (!apiTypeCode) {
      setError('Internal error: missing basket type code')
      return
    }

    setLoading(true)
    try {
      const fn = mode === 'increase' ? increaseBasketRaw : decreaseBasketRaw
      await fn(apiTypeCode, cleanSymbol, value)
      setSuccess(true)
      onSuccess?.()
      setTimeout(onClose, 700)
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.header}>
          <div>
            <div className={styles.title}>
              {isEditingExisting ? `Adjust ${symbol}` : `New ${label} Basket`}
            </div>
            <div className={styles.subtitle} style={{ textTransform: 'capitalize' }}>{type} basket</div>
          </div>
          <button className={styles.closeBtn} onClick={onClose}><IconClose /></button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className={styles.body}>
          {success ? (
            <div className={styles.successMsg}>
              ✅ {mode === 'increase' ? 'Increased' : 'Decreased'} successfully
            </div>
          ) : (
            <>
              {error && <div className={styles.error}>⚠️ {error}</div>}

              {/* Mode toggle */}
              <div className={styles.toggleRow}>
                <button
                  type="button"
                  className={`${styles.toggleBtn} ${mode === 'increase' ? styles.toggleActive : ''}`}
                  onClick={() => setMode('increase')}
                >
                  + Increase
                </button>
                <button
                  type="button"
                  className={`${styles.toggleBtn} ${mode === 'decrease' ? styles.toggleActiveRed : ''}`}
                  onClick={() => setMode('decrease')}
                >
                  − Decrease
                </button>
              </div>

              {/* Symbol */}
              <div className={styles.field}>
                <label className={styles.label}>Symbol</label>
                <input
                  className={styles.input}
                  placeholder={type === 'currency' ? 'e.g. USD' : type === 'gold' ? 'e.g. IR_GOLD_18K' : 'e.g. BTC'}
                  value={symbol}
                  onChange={e => setSymbol(e.target.value)}
                  disabled={isEditingExisting}
                  autoFocus={!isEditingExisting}
                  style={{ textTransform: 'uppercase' }}
                />
              </div>

              {/* Value */}
              <div className={styles.field}>
                <label className={styles.label}>Amount</label>
                <input
                  className={styles.input}
                  type="number"
                  step="any"
                  min="0"
                  placeholder="0.00"
                  value={value}
                  onChange={e => setValue(e.target.value)}
                  autoFocus={isEditingExisting}
                />
              </div>

              <button
                type="submit"
                className={`${styles.submitBtn} ${styles[`submit_${color}`]} ${loading ? styles.loading : ''}`}
                disabled={loading}
              >
                {loading ? <span className={styles.spinner} /> : (mode === 'increase' ? 'Add to basket' : 'Remove from basket')}
              </button>

              {!isEditingExisting && (
                <p className={styles.hint}>
                  If this basket doesn't exist yet, it will be created automatically.
                </p>
              )}
            </>
          )}
        </form>
      </div>
    </div>
  )
}
