const BASE = '/api'

let streamlitBridge = null

export function configureStreamlitBridge(bridge) {
  streamlitBridge = bridge
}

function authHeaders() {
  const token = localStorage.getItem('nypiel_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function handle(res) {
  if (!res.ok) {
    let detail = 'Something went wrong. Please try again.'
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {
      /* no-op */
    }
    throw new Error(detail)
  }
  return res.json()
}

export const api = {
  signup: (email, password, name) =>
    streamlitBridge
      ? streamlitBridge('signup', { email, password, name })
      : fetch(`${BASE}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name }),
    }).then(handle),

  login: (email, password) =>
    streamlitBridge
      ? streamlitBridge('login', { email, password })
      : fetch(`${BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    }).then(handle),

  me: () => streamlitBridge
    ? streamlitBridge('me', {})
    : fetch(`${BASE}/auth/me`, { headers: authHeaders() }).then(handle),

  analyze: (file, save = true) => {
    if (streamlitBridge) {
      return fileToDataUrl(file).then((image) =>
        streamlitBridge('analyze', { image, save }),
      )
    }
    const form = new FormData()
    form.append('file', file)
    return fetch(`${BASE}/scan/analyze?save=${save}`, {
      method: 'POST',
      headers: authHeaders(),
      body: form,
    }).then(handle)
  },

  history: () => streamlitBridge
    ? streamlitBridge('history', {})
    : fetch(`${BASE}/scan/history`, { headers: authHeaders() }).then(handle),

  getScan: (id) => streamlitBridge
    ? streamlitBridge('getScan', { id })
    : fetch(`${BASE}/scan/${id}`, { headers: authHeaders() }).then(handle),

  deleteScan: (id) =>
    streamlitBridge
      ? streamlitBridge('deleteScan', { id })
      : fetch(`${BASE}/scan/${id}`, { method: 'DELETE', headers: authHeaders() }).then(handle),

  ask: (message, scanId) =>
    streamlitBridge
      ? streamlitBridge('ask', { message, scanId: scanId ?? null })
      : fetch(`${BASE}/chat/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ message, scan_id: scanId ?? null }),
    }).then(handle),
}

function fileToDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = () => reject(new Error('Could not read the selected image.'))
    reader.readAsDataURL(file)
  })
}
