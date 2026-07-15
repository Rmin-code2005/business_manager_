import { useState } from 'react'
import { updateTelegramUsername } from '../api/auth'
import { useAuth } from '../context/AuthContext'
import styles from './EditableTelegramRow.module.css'

function IconEdit() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
      <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
    </svg>
  )
}

function IconCheck() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  )
}

function IconX() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
      <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  )
}

// Normalize: ensure it starts with @ (or is empty)
function normalizeUsername(raw) {
  const trimmed = raw.trim()
  if (!trimmed) return ''
  return trimmed.startsWith('@') ? trimmed : `@${trimmed}`
}

export default function EditableTelegramRow({ value }) {
  const { refreshUser } = useAuth()
  const [editing, setEditing]   = useState(false)
  const [draft, setDraft]       = useState(value || '')
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')

  function startEdit() {
    setDraft(value || '')
    setError('')
    setEditing(true)
  }

  function cancelEdit() {
    setEditing(false)
    setError('')
  }

  async function handleSave() {
    const normalized = normalizeUsername(draft)
    if (!normalized) {
      setError('Username cannot be empty')
      return
    }
    if (!/^@[a-zA-Z0-9_]{5,32}$/.test(normalized)) {
      setError('Use 5-32 letters, numbers, or underscores')
      return
    }

    setLoading(true)
    setError('')
    try {
      await updateTelegramUsername(normalized)
      await refreshUser()
      setEditing(false)
    } catch (err) {
      setError(err.message || 'Failed to update')
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') { e.preventDefault(); handleSave() }
    if (e.key === 'Escape') cancelEdit()
  }

  return (
    <div className={styles.row}>
      <span className={styles.label}>Telegram</span>

      {editing ? (
        <div className={styles.editArea}>
          <div className={styles.inputWrap}>
            <input
              className={styles.input}
              value={draft}
              onChange={e => setDraft(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="@username"
              autoFocus
              disabled={loading}
            />
            <button className={styles.iconBtn} onClick={handleSave} disabled={loading} title="Save">
              {loading ? <span className={styles.spinner} /> : <IconCheck />}
            </button>
            <button className={`${styles.iconBtn} ${styles.iconBtnGhost}`} onClick={cancelEdit} disabled={loading} title="Cancel">
              <IconX />
            </button>
          </div>
          {error && <span className={styles.error}>{error}</span>}
        </div>
      ) : (
        <button className={styles.valueBtn} onClick={startEdit}>
          <span className={styles.value}>
            {value || <em style={{ color: 'var(--text-muted)', fontStyle: 'normal' }}>Not set</em>}
          </span>
          <span className={styles.editIcon}><IconEdit /></span>
        </button>
      )}
    </div>
  )
}
