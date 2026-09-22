import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import ArchMark from '../components/ArchMark'

export default function Signup() {
  const { signup } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      await signup(email, password, name)
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
      <h1 className="font-display text-3xl text-walnut text-center mb-1">Create your account</h1>
      <p className="text-sm text-clay text-center mb-8">Save every scan and track your skin over time.</p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="text-xs tracking-wide text-olive uppercase">Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 w-full border border-olive/30 rounded-xl px-4 py-2.5 bg-white/60 focus:border-walnut outline-none"
          />
        </div>
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
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full border border-olive/30 rounded-xl px-4 py-2.5 bg-white/60 focus:border-walnut outline-none"
          />
          <p className="text-xs text-clay mt-1">At least 8 characters.</p>
        </div>

        {error && <p className="text-sm text-rust">{error}</p>}

        <button
          type="submit"
          disabled={busy}
          className="w-full bg-walnut text-cream rounded-full py-2.5 text-sm hover:bg-clay transition-colors disabled:opacity-60"
        >
          {busy ? 'Creating account…' : 'Create account'}
        </button>
      </form>

      <p className="text-sm text-clay text-center mt-6">
        Already have an account?{' '}
        <Link to="/login" className="text-walnut underline underline-offset-4">
          Log in
        </Link>
      </p>
    </div>
  )
}
