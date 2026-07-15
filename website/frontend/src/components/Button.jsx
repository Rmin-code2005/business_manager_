import styles from './Button.module.css'

/**
 * Props:
 *   variant   'primary' | 'ghost'   (default: primary)
 *   loading   boolean
 *   ...rest   passed to <button>
 */
export default function Button({ children, variant = 'primary', loading = false, ...rest }) {
  return (
    <button
      className={`${styles.btn} ${styles[variant]} ${loading ? styles.loading : ''}`}
      disabled={loading || rest.disabled}
      {...rest}
    >
      {loading ? <span className={styles.spinner} /> : children}
    </button>
  )
}
