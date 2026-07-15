import styles from './Input.module.css'

/**
 * Controlled input with label + optional error message.
 *
 * Props:
 *   label      string
 *   error      string | null
 *   id         string
 *   ...rest    passed to <input>
 */
export default function Input({ label, error, id, ...rest }) {
  return (
    <div className={styles.wrapper}>
      {label && <label htmlFor={id} className={styles.label}>{label}</label>}
      <input
        id={id}
        className={`${styles.input} ${error ? styles.inputError : ''}`}
        {...rest}
      />
      {error && <span className={styles.error}>{error}</span>}
    </div>
  )
}
