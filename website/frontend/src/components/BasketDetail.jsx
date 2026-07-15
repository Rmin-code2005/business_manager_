import { useState, useEffect } from 'react'
import styles from './BasketDetail.module.css'

function IconClose() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
      <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  )
}

function formatNum(val) {
  if (val === undefined || val === null || val === '' || val === '-') return '—'
  const n = Number(val)
  if (isNaN(n)) return val
  return n.toLocaleString('en-US')
}

/**
 * Props:
 *   symbol     string          e.g. "BTC"
 *   type       string          'crypto' | 'currency' | 'gold'
 *   color      string          'blue' | 'green' | 'yellow'
 *   fetchFn    async (symbol) => detail
 *   onClose    fn
 *   onAdjust   fn()            opens the adjust modal for this symbol
 */
export default function BasketDetail({ symbol, type, color, fetchFn, onClose, onAdjust }) {
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState(null)

  useEffect(() => {
    fetchFn(symbol)
      .then(setData)
      .catch(err => setError(err.message || 'Failed to load'))
      .finally(() => setLoading(false))
  }, [symbol, fetchFn])

  // Close on Escape key
  useEffect(() => {
    function onKey(e) { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <span className={`${styles.badge} ${styles[`badge_${color}`]}`}>{symbol}</span>
            <div>
              <div className={styles.title}>Basket Detail</div>
              <div className={styles.subtitle} style={{ textTransform: 'capitalize' }}>{type} basket</div>
            </div>
          </div>
          <button className={styles.closeBtn} onClick={onClose}><IconClose /></button>
        </div>

        {/* Body */}
        <div className={styles.body}>
          {loading ? (
            <div className={styles.skeletons}>
              {[1,2,3,4].map(i => (
                <div key={i} className={styles.skeletonRow}>
                  <div className={styles.skeletonLabel} />
                  <div className={styles.skeletonValue} />
                </div>
              ))}
            </div>
          ) : error ? (
            <div className={styles.error}>⚠️ {error}</div>
          ) : (
            <>
              <div className={styles.fields}>
                <DetailRow label="Name"            value={data?.name} />
                <DetailRow label="Count"           value={formatNum(data?.count)} />
                <DetailRow label="Start Price (T)" value={formatNum(data?.start_price_T)} suffix="Toman" color={color} />
                <DetailRow label="Start Price ($)" value={formatNum(data?.start_price_D)} suffix="USD" color={color} />
              </div>
              {onAdjust && (
                <button className={`${styles.adjustBtn} ${styles[`adjustBtn_${color}`]}`} onClick={onAdjust}>
                  Adjust amount
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function DetailRow({ label, value, suffix, color }) {
  return (
    <div className={styles.row}>
      <span className={styles.rowLabel}>{label}</span>
      <span className={styles.rowValue}>
        {value ?? '—'}
        {suffix && value && value !== '—' && (
          <span className={styles.suffix}> {suffix}</span>
        )}
      </span>
    </div>
  )
}
