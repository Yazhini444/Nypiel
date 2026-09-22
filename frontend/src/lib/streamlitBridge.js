import { Streamlit } from 'streamlit-component-lib'

let requestNumber = 0
const pending = new Map()

export function createStreamlitBridge() {
  const bridge = (action, payload) => {
    const requestId = `request-${Date.now()}-${requestNumber++}`
    return new Promise((resolve, reject) => {
      pending.set(requestId, { resolve, reject })
      Streamlit.setComponentValue({ requestId, action, payload })
    })
  }

  const handleRender = (event) => {
    const currentUser = event.detail?.args?.currentUser || null
    if (currentUser) {
      localStorage.setItem('nypiel_streamlit_user', JSON.stringify(currentUser))
      if (window.location.hash === '#/signup' || window.location.hash === '#/login' || !window.location.hash) {
        window.location.hash = '#/scan'
      }
    } else {
      localStorage.removeItem('nypiel_streamlit_user')
    }
    window.dispatchEvent(new CustomEvent('nypiel-auth-updated'))

    const response = event.detail?.args?.bridgeResponse
    if (!response) return
    if (response.ok) {
      localStorage.removeItem('nypiel_streamlit_error')
    } else if (response.error) {
      localStorage.setItem('nypiel_streamlit_error', response.error)
      window.dispatchEvent(new CustomEvent('nypiel-bridge-error'))
    }
    const request = pending.get(response.requestId)
    if (!request) return
    pending.delete(response.requestId)
    if (response.ok) request.resolve(response.data)
    else request.reject(new Error(response.error || 'Nypiel request failed.'))
  }

  Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, handleRender)
  Streamlit.setFrameHeight()
  return bridge
}

export function cleanupStreamlitBridge() {
  pending.forEach(({ reject }) => reject(new Error('Nypiel component closed.')))
  pending.clear()
}

export function getStreamlitBridgeError() {
  return localStorage.getItem('nypiel_streamlit_error') || ''
}