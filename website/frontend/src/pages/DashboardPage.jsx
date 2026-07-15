import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import PricesPanel from '../components/PricesPanel'
import BasketsSection from '../components/BasketsSection'
import TelegramUsernameRow from '../components/TelegramUsernameRow'
import EditableProfileRow from '../components/EditableProfileRow'
import { getCryptoPrices, getCurrencyPrices, getGoldPrices, updateUserInfo } from '../api/auth'
import styles from './DashboardPage.module.css'

function IconLogout() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
      <polyline points="16 17 21 12 16 7"/>
      <line x1="21" y1="12" x2="9" y2="12"/>
    </svg>
  )
}

export default function DashboardPage() {
  const { user, onLogout, refreshUser } = useAuth()
  const navigate = useNavigate()
  const [profileOpen, setProfileOpen] = useState(false)
  const dropdownRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setProfileOpen(false)
      }
    }
    if (profileOpen) document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [profileOpen])

  function handleLogout() {
    setProfileOpen(false)
    onLogout()
    navigate('/login', { replace: true })
  }

  const initials = [user?.first_name?.[0], user?.last_name?.[0]]
    .filter(Boolean).join('').toUpperCase() || '?'
  const fullName = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || user?.email

  return (
    <div className={styles.shell}>
      {/* ── Navbar ── */}
      <header className={styles.nav}>
        <div className={styles.navBrand}>
          <div className={styles.navLogo}>BM</div>
          <span className={styles.navName}>Bissinus Manager</span>
        </div>

        <div className={styles.userArea} ref={dropdownRef}>
          <button className={styles.userBtn} onClick={() => setProfileOpen(o => !o)}>
            <div className={styles.avatar}>{initials}</div>
            <div className={styles.userInfo}>
              <span className={styles.userName}>{fullName}</span>
              {user?.email && <span className={styles.userEmail}>{user.email}</span>}
            </div>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
              className={`${styles.chevron} ${profileOpen ? styles.chevronOpen : ''}`}>
              <path d="M6 9l6 6 6-6"/>
            </svg>
          </button>

          {profileOpen && (
            <div className={styles.dropdown}>
              <div className={styles.dropdownHeader}>
                <div className={styles.dropdownAvatar}>{initials}</div>
                <div>
                  <div className={styles.dropdownName}>{fullName}</div>
                  <div className={styles.dropdownEmail}>{user?.email}</div>
                </div>
              </div>
              <hr className={styles.dropdownDivider} />
              <button className={styles.logoutBtn} onClick={handleLogout}>
                <IconLogout /> Sign out
              </button>
            </div>
          )}
        </div>
      </header>

      {/* ── Main ── */}
      <main className={styles.main}>
        <div className={styles.welcome}>
          <h1 className={styles.welcomeTitle}>
            Welcome, <span className={styles.accent}>{user?.first_name || 'there'}</span> 👋
          </h1>
          <p className={styles.welcomeSub}>Live market prices</p>
        </div>

        {/* ── 3 price panels ── */}
        <div className={styles.pricesGrid}>
          <PricesPanel
            title="Currency"
            icon="💵"
            color="blue"
            fetchFn={getCurrencyPrices}
            unit="Toman"
          />
          <PricesPanel
            title="Gold"
            icon="🥇"
            color="yellow"
            fetchFn={getGoldPrices}
            unit="Toman"
          />
          <PricesPanel
            title="Crypto"
            icon="₿"
            color="green"
            fetchFn={getCryptoPrices}
            unit="Toman"
          />
        </div>

        {/* ── Baskets ── */}
        <BasketsSection />

        {/* ── Profile card ── */}
        <div className={styles.module}>
          <div className={styles.moduleHeader}>
            <span className={styles.moduleTitle}>Your Profile</span>
          </div>
          <div className={styles.profileFields}>
            <EditableProfileRow label="First name" field="first_name" value={user?.first_name} type="text"  saveFn={updateUserInfo} onSaved={refreshUser} />
            <EditableProfileRow label="Last name"  field="last_name"  value={user?.last_name}  type="text"  saveFn={updateUserInfo} onSaved={refreshUser} />
            <EditableProfileRow label="Email"      field="email"      value={user?.email}      type="email" saveFn={updateUserInfo} onSaved={refreshUser} />
            <EditableProfileRow label="Phone"      field="phone"      value={user?.phone}      type="tel"   saveFn={updateUserInfo} onSaved={refreshUser} />
            <ProfileRow label="Gender" value={user?.gender} capitalize />
            <TelegramUsernameRow value={user?.telegram_username} onUpdated={refreshUser} />
          </div>
        </div>
      </main>
    </div>
  )
}

function ProfileRow({ label, value, capitalize }) {
  return (
    <div className={styles.profileRow}>
      <span className={styles.profileLabel}>{label}</span>
      <span className={styles.profileValue} style={capitalize ? { textTransform: 'capitalize' } : {}}>
        {value || <em style={{ color: 'var(--text-muted)', fontStyle: 'normal' }}>—</em>}
      </span>
    </div>
  )
}
