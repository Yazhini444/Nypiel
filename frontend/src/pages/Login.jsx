import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import ArchMark from '../components/ArchMark'
import { getStreamlitBridgeError } from '../lib/streamlitBridge'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(getStreamlitBridgeError)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    const showBridgeError = () => setError(getStreamlitBridgeError())
    window.addEventListener('nypiel-bridge-error', showBridgeError)
    return () => window.removeEventListener('nypiel-bridge-error', showBridgeError)
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    localStorage.removeItem('nypiel_streamlit_error')
    setBusy(true)
    try {
      await login(email, password)
      navigate('/scan')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="max-w-sm mx-auto px-6 py-20">
      <div className="flex justify-center text-olive mb-6">
        <ArchMark className="w-9 h-12" />
      </div>
      <h1 className="font-display text-3xl text-walnut text-center mb-1">Welcome back</h1>
      <p className="text-sm text-clay text-center mb-8">Log in to see your saved skin results.</p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="text-xs tracking-wide text-olive uppercase">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full border border-olive/30 rounded-xl px-4 py-2.5 bg-white/60 focus:border-walnut outline-none"
          />
        </div>
        <div>
          <label className="text-xs tracking-wide text-olive uppercase">Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full border border-olive/30 rounded-xl px-4 py-2.5 bg-white/60 focus:border-walnut outline-none"
          />
        </div>

        {error && <p className="text-sm text-rust">{error}</p>}

        <button
          type="submit"
          disabled={busy}
          className="w-full bg-walnut text-cream rounded-full py-2.5 text-sm hover:bg-clay transition-colors disabled:opacity-60"
        >
          {busy ? 'Logging in…' : 'Log in'}
        </button>
      </form>

      <p className="text-sm text-clay text-center mt-6">
        New to nypiel?{' '}
        <Link to="/signup" className="text-walnut underline underline-offset-4">
          Create an account
        </Link>
      </p>
    </div>
  )
}
