import React, { createContext, useContext, useEffect, useState } from 'react'
import { api } from '../lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children, skipInitialCheck = false }) {
  const [user, setUser] = useState(() => {
    if (!skipInitialCheck) return null
    try {
      return JSON.parse(localStorage.getItem('nypiel_streamlit_user') || 'null')
    } catch {
      return null
    }
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (skipInitialCheck) {
      const syncStreamlitUser = () => {
        try {
          setUser(JSON.parse(localStorage.getItem('nypiel_streamlit_user') || 'null'))
        } catch {
          setUser(null)
        }
      }
      window.addEventListener('nypiel-auth-updated', syncStreamlitUser)
      syncStreamlitUser()
      setLoading(false)
      return () => window.removeEventListener('nypiel-auth-updated', syncStreamlitUser)
    }
    const token = localStorage.getItem('nypiel_token')
    if (!token) {
      setLoading(false)
      return
    }
    api
      .me()
      .then(setUser)
      .catch(() => localStorage.removeItem('nypiel_token'))
      .finally(() => setLoading(false))
  }, [])

  function persist(token, user) {
    localStorage.setItem('nypiel_token', token)
    localStorage.setItem('nypiel_streamlit_user', JSON.stringify(user))
    setUser(user)
  }

  async function login(email, password) {
    const data = await api.login(email, password)
    persist(data.access_token, data.user)
  }

  async function signup(email, password, name) {
    const data = await api.signup(email, password, name)
    persist(data.access_token, data.user)
  }

  function logout() {
    localStorage.removeItem('nypiel_token')
    localStorage.removeItem('nypiel_streamlit_user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
