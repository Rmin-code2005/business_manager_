import { useState } from 'react'
import { updateTelegramUsername } from '../api/auth'
import styles from './TelegramUsernameRow.module.css'

function IconEdit() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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

/**
 * Props:
 *   value      string|null   current telegram_username from user object
 *   onUpdated  fn(newValue)  called after a successful save, to update parent state
 */
export default function TelegramUsernameRow({ value, onUpdated }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft]     = useState(value || '')
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  function startEdit() {
    setDraft(value || '')
    setError('')
    setEditing(true)
  }

  function cancelEdit() {
    setEditing(false)
    setError('')
    setDraft(value || '')
  }

  async function handleSave() {
    setError('')
    let clean = draft.trim()

    if (!clean) {
      setError('Username cannot be empty')
      return
    }
    // Normalize: ensure it starts with @
    if (!clean.startsWith('@')) clean = '@' + clean

    setLoading(true)
    try {
      await updateTelegramUsername(clean)
      onUpdated?.(clean)
      setEditing(false)
    } catch (err) {
      setError(err.message || 'Failed to update')
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') handleSave()
    if (e.key === 'Escape') cancelEdit()
  }

  return (
    <div className={styles.row}>
      <span className={styles.label}>Telegram</span>

      {editing ? (
        <div className={styles.editArea}>
          <div className={styles.inputGroup}>
            <input
              className={styles.input}
              value={draft}
              onChange={e => setDraft(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="@username"
              autoFocus
              disabled={loading}
            />
            <button
              className={styles.iconBtn}
              onClick={handleSave}
              disabled={loading}
              title="Save"
            >
              {loading ? <span className={styles.spinner} /> : <IconCheck />}
            </button>
            <button
              className={`${styles.iconBtn} ${styles.cancelBtn}`}
              onClick={cancelEdit}
              disabled={loading}
              title="Cancel"
            >
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
