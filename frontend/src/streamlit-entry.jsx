import React from 'react'
import ReactDOM from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import { Streamlit, withStreamlitConnection } from 'streamlit-component-lib'
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx'
import { configureStreamlitBridge } from './lib/api.js'
import { createStreamlitBridge } from './lib/streamlitBridge.js'
import './index.css'
import './streamlit.css'

const savedRoute = localStorage.getItem('nypiel_streamlit_route')
if (savedRoute && window.location.hash !== savedRoute) {
  window.location.hash = savedRoute
}
window.addEventListener('hashchange', () => {
  localStorage.setItem('nypiel_streamlit_route', window.location.hash || '#/')
})

configureStreamlitBridge(createStreamlitBridge())

function StreamlitApp() {
  React.useEffect(() => {
    Streamlit.setFrameHeight()
  })

  return (
    <React.StrictMode>
      <HashRouter>
        <AuthProvider skipInitialCheck>
          <App />
        </AuthProvider>
      </HashRouter>
    </React.StrictMode>
  )
}

const ConnectedApp = withStreamlitConnection(StreamlitApp)
ReactDOM.createRoot(document.getElementById('root')).render(<ConnectedApp />)