// ─── Base URL ─────────────────────────────────────────────────────────────────
// Change this to your Django backend URL in production.
// In development, Vite proxies /api → http://localhost:8000
const BASE = ''

// ─── Token helpers ────────────────────────────────────────────────────────────
export const token = {
  getAccess:  () => localStorage.getItem('access_token'),
  getRefresh: () => localStorage.getItem('refresh_token'),
  setTokens:  (access, refresh) => {
    localStorage.setItem('access_token', access)
    if (refresh) localStorage.setItem('refresh_token', refresh)
  },
  clear: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },
}

// ─── Raw fetch wrapper ────────────────────────────────────────────────────────
async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })

  // 204 No Content — nothing to parse
  if (res.status === 204) return null

  const data = await res.json()

  if (!res.ok) {
    // DEBUG: log full request/response details to find the real source of errors
    console.error('[API ERROR]', {
      url: `${BASE}${path}`,
      method: options.method || 'GET',
      sentBody: options.body,
      status: res.status,
      response: data,
    })
    // Build a readable error message from DRF response
    const msg = extractError(data) || `HTTP ${res.status}`
    const err = new Error(msg)
    err.status = res.status
    err.data = data
    throw err
  }

  return data
}

function extractError(data) {
  if (!data) return null
  if (typeof data === 'string') return data
  // DRF often returns { detail: '...' } or { field: ['error'] }
  if (data.detail) return data.detail
  const msgs = Object.entries(data)
    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
  return msgs.join(' | ')
}

// ─── Authenticated fetch (auto refresh) ───────────────────────────────────────
async function authRequest(path, options = {}) {
  const accessToken = token.getAccess()
  try {
    return await request(path, {
      ...options,
      headers: { Authorization: `Bearer ${accessToken}`, ...options.headers },
    })
  } catch (err) {
    // 401 → try to refresh once
    if (err.status === 401) {
      const refreshToken = token.getRefresh()
      if (!refreshToken) throw err

      try {
        const refreshed = await request('/api/token/refresh/', {
          method: 'POST',
          body: JSON.stringify({ refresh: refreshToken }),
        })
        token.setTokens(refreshed.access, null)

        // Retry original request with new access token
        return await request(path, {
          ...options,
          headers: { Authorization: `Bearer ${refreshed.access}`, ...options.headers },
        })
      } catch {
        token.clear()
        window.location.href = '/login'
        throw err
      }
    }
    throw err
  }
}

// ─── Auth endpoints ───────────────────────────────────────────────────────────

/**
 * Login with email + password.
 * Returns { access, refresh, user: { id, email, first_name } }
 */
export async function login(email, password) {
  const data = await request('/api/login/', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
  token.setTokens(data.access, data.refresh)
  return data
}

/**
 * Logout — just clears local tokens (no server-side blacklist endpoint yet).
 */
export function logout() {
  token.clear()
}

// ─── User endpoints ───────────────────────────────────────────────────────────

/**
 * GET /api/me/
 * Returns UserDetail: { phone, email, first_name, last_name, gender, telegram_username }
 */
export async function getMe() {
  return authRequest('/api/me/')
}

/**
 * PATCH /api/update-telegram-username/
 * Body: { telegram_username: "@armin_ghajari" }
 */
export async function updateTelegramUsername(telegramUsername) {
  return authRequest('/api/update-telegram-username/', {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ telegram_username: telegramUsername }),
  })
}

/**
 * PATCH /api/me/change-info/
 * Body: one or more of { first_name, last_name, phone, email }
 */
export async function updateUserInfo(fields) {
  return authRequest('/api/me/change-info/', {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(fields),
  })
}

// ─── Prices endpoints ─────────────────────────────────────────────────────────

export async function getCryptoPrices() {
  return authRequest('/api/crypto/prices/')
}

export async function getCurrencyPrices() {
  return authRequest('/api/currency/prices/')
}

export async function getGoldPrices() {
  return authRequest('/api/gold/prices/')
}

// ─── Basket list endpoints ────────────────────────────────────────────────────

export async function getCryptoBaskets() {
  return authRequest('/api/user/crypto-basket/')
}

export async function getCurrencyBaskets() {
  return authRequest('/api/user/currency-basket/')
}

export async function getGoldBaskets() {
  return authRequest('/api/user/gold-basket/')
}

// ─── Basket detail endpoints ──────────────────────────────────────────────────

export async function getCryptoBasketDetail(symbol) {
  return authRequest(`/api/user/crypto-basket/${symbol}`)
}

export async function getCurrencyBasketDetail(symbol) {
  return authRequest(`/api/user/currency-basket/${symbol}`)
}

export async function getGoldBasketDetail(symbol) {
  return authRequest(`/api/user/gold-basket/${symbol}`)
}

// ─── Increase / Decrease basket value (RAW — exact backend code, no mapping) ──
// typeCode must be exactly one of: 'cr' (crypto), 'ca' (currency/cash), 'g' (gold)
// This is the source of truth — callers must pass the correct short code directly.

export async function increaseBasketRaw(typeCode, symbol, value) {
  console.log('[increaseBasketRaw] sending →', { type: typeCode, symbol, value })
  return authRequest('/api/user/basket/increase/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type: typeCode, symbol, value }),
  })
}

export async function decreaseBasketRaw(typeCode, symbol, value) {
  console.log('[decreaseBasketRaw] sending →', { type: typeCode, symbol, value })
  return authRequest('/api/user/basket/decrease/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type: typeCode, symbol, value }),
  })
}
