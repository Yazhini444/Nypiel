import React, { createContext, useContext, useEffect, useState } from 'react'
import { api } from '../lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
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
