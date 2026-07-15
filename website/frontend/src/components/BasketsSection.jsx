import { useState, useEffect, useCallback } from 'react'
import BasketDetail from './BasketDetail'
import BasketAdjustModal from './BasketAdjustModal'
import styles from './BasketsSection.module.css'
import {
  getCryptoBaskets, getCurrencyBaskets, getGoldBaskets,
  getCryptoBasketDetail, getCurrencyBasketDetail, getGoldBasketDetail,
} from '../api/auth'

const BASKET_TYPES = [
  {
    key: 'currency',
    apiTypeCode: 'ca',   // backend code for Currency/Cash basket
    label: 'Currency Baskets',
    icon: '💵',
    color: 'blue',
    listFn: getCurrencyBaskets,
    detailFn: getCurrencyBasketDetail,
  },
  {
    key: 'gold',
    apiTypeCode: 'g',    // backend code for Gold basket
    label: 'Gold Baskets',
    icon: '🥇',
    color: 'yellow',
    listFn: getGoldBaskets,
    detailFn: getGoldBasketDetail,
  },
  {
    key: 'crypto',
    apiTypeCode: 'cr',   // backend code for Crypto basket
    label: 'Crypto Baskets',
    icon: '₿',
    color: 'green',
    listFn: getCryptoBaskets,
    detailFn: getCryptoBasketDetail,
  },
]

export default function BasketsSection() {
  // detail modal state: { symbol, type, color, detailFn } | null
  const [selected, setSelected] = useState(null)
  // adjust modal state: { type, color, label, initialSymbol } | null
  const [adjusting, setAdjusting] = useState(null)
  // bump this to force all lists to refetch after a successful adjust
  const [refreshKey, setRefreshKey] = useState(0)

  function handleAdjustSuccess() {
    setRefreshKey(k => k + 1)
  }

  return (
    <div className={styles.section}>
      <div className={styles.sectionHeader}>
        <h2 className={styles.sectionTitle}>My Baskets</h2>
      </div>

      <div className={styles.grid}>
        {BASKET_TYPES.map(t => (
          <BasketList
            key={t.key}
            {...t}
            refreshKey={refreshKey}
            onSelect={(symbol) => setSelected({
              symbol, type: t.key, color: t.color, detailFn: t.detailFn,
            })}
            onAdd={() => setAdjusting({
              type: t.key, apiTypeCode: t.apiTypeCode, color: t.color, label: t.label, initialSymbol: '',
            })}
          />
        ))}
      </div>

      {selected && (
        <BasketDetail
          symbol={selected.symbol}
          type={selected.type}
          color={selected.color}
          fetchFn={selected.detailFn}
          onClose={() => setSelected(null)}
          onAdjust={() => {
            const cfg = BASKET_TYPES.find(t => t.key === selected.type)
            setAdjusting({
              type: selected.type,
              apiTypeCode: cfg?.apiTypeCode,
              color: selected.color,
              label: cfg?.label,
              initialSymbol: selected.symbol,
            })
            setSelected(null)
          }}
        />
      )}

      {adjusting && (
        <BasketAdjustModal
          type={adjusting.type}
          apiTypeCode={adjusting.apiTypeCode}
          color={adjusting.color}
          label={adjusting.label}
          initialSymbol={adjusting.initialSymbol}
          onClose={() => setAdjusting(null)}
          onSuccess={handleAdjustSuccess}
        />
      )}
    </div>
  )
}

// ─── Single basket type list ──────────────────────────────────────────────────
function BasketList({ label, icon, color, type, listFn, refreshKey, onSelect, onAdd }) {
  const [items, setItems]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    setLoading(true)
    listFn()
      .then(data => setItems(Array.isArray(data) ? data : []))
      .catch(err => setError(err.message || 'Failed to load'))
      .finally(() => setLoading(false))
  }, [listFn, refreshKey])

  return (
    <div className={`${styles.card} ${styles[`card_${color}`]}`}>
      <div className={styles.cardHeader}>
        <span className={styles.cardIcon}>{icon}</span>
        <span className={styles.cardTitle}>{label}</span>
        <span className={styles.cardCount}>{items ? items.length : '—'}</span>
        <button
          className={`${styles.addBtn} ${styles[`addBtn_${color}`]}`}
          onClick={onAdd}
          title={`Add ${label}`}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        </button>
      </div>

      <div className={styles.cardBody}>
        {loading ? (
          <div className={styles.skeletons}>
            {[1,2,3].map(i => <div key={i} className={styles.skeletonChip} />)}
          </div>
        ) : error ? (
          <div className={styles.empty}>⚠️ {error}</div>
        ) : items.length === 0 ? (
          <div className={styles.empty}>No baskets yet — tap + to add one</div>
        ) : (
          <div className={styles.chips}>
            {items.map(item => (
              <button
                key={item.name}
                className={`${styles.chip} ${styles[`chip_${color}`]}`}
                onClick={() => onSelect(item.name)}
              >
                {item.name}
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M9 18l6-6-6-6"/>
                </svg>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
