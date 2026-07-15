import { useState, useEffect, useCallback } from 'react'
import styles from './PricesPanel.module.css'

function IconRefresh({ spinning }) {
  return (
    <svg
      width="14" height="14" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"
      className={spinning ? styles.spinning : ''}
    >
      <polyline points="23 4 23 10 17 10"/>
      <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
    </svg>
  )
}

// Format big numbers with comma separators
function formatNumber(val) {
  if (val === undefined || val === null || val === '') return '—'
  const num = Number(val)
  if (isNaN(num)) return val
  return num.toLocaleString('en-US')
}

/**
 * Props:
 *   title      string         e.g. "Currency"
 *   icon       string         emoji e.g. "💵"
 *   color      string         'blue' | 'green' | 'yellow'
 *   fetchFn    async fn       the API call
 *   unit       string         e.g. "تومان" shown after price
 */
export default function PricesPanel({ title, icon, color, fetchFn, unit = '' }) {
  const [prices, setPrices]   = useState(null)   // { SYMBOL: { current, min, max, update } }
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)
  const [lastUpdate, setLastUpdate] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetchFn()
      // res.data.prices  or  res.prices  — handle both shapes
      const prices = res?.data?.prices ?? res?.prices ?? res
      setPrices(prices)
      setLastUpdate(new Date())
    } catch (err) {
      setError(err.message || 'Failed to load')
    } finally {
      setLoading(false)
    }
  }, [fetchFn])

  // Load on mount
  useEffect(() => { load() }, [load])

  const entries = prices ? Object.entries(prices) : []

  return (
    <div className={`${styles.panel} ${styles[`panel_${color}`]}`}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.icon}>{icon}</span>
          <span className={styles.title}>{title}</span>
          {lastUpdate && !loading && (
            <span className={styles.updated}>
              {lastUpdate.toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </span>
          )}
        </div>
        <button
          className={styles.refreshBtn}
          onClick={load}
          disabled={loading}
          title="Refresh"
        >
          <IconRefresh spinning={loading} />
        </button>
      </div>

      {/* Body */}
      <div className={styles.body}>
        {error ? (
          <div className={styles.error}>
            <span>⚠️</span> {error}
          </div>
        ) : loading && !prices ? (
          /* Skeleton */
          <div className={styles.skeletons}>
            {[1,2,3,4].map(i => (
              <div key={i} className={styles.skeletonRow}>
                <div className={styles.skeletonLabel} />
                <div className={styles.skeletonValue} />
              </div>
            ))}
          </div>
        ) : entries.length === 0 ? (
          <div className={styles.empty}>No data available</div>
        ) : (
          <div className={styles.rows}>
            {entries.map(([symbol, data]) => (
              <PriceRow
                key={symbol}
                symbol={symbol}
                current={data.current}
                min1h={data.min?.['1hour']}
                max1h={data.max?.['1hour']}
                update={data.update}
                unit={unit}
                color={color}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function PriceRow({ symbol, current, min1h, max1h, unit, color }) {
  return (
    <div className={styles.row}>
      <div className={styles.rowLeft}>
        <span className={`${styles.symbol} ${styles[`symbol_${color}`]}`}>{symbol}</span>
      </div>
      <div className={styles.rowRight}>
        <span className={styles.current}>
          {formatNumber(current)}
          {unit && <span className={styles.unit}> {unit}</span>}
        </span>
        <div className={styles.range}>
          <span className={styles.minVal}>↓ {formatNumber(min1h)}</span>
          <span className={styles.rangeSep}>·</span>
          <span className={styles.maxVal}>↑ {formatNumber(max1h)}</span>
        </div>
      </div>
    </div>
  )
}
