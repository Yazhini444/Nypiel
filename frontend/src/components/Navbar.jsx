import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import ArchMark from './ArchMark'

const linkClass = ({ isActive }) =>
  `text-sm tracking-wide transition-colors ${
    isActive ? 'text-walnut font-medium' : 'text-clay hover:text-walnut'
  }`

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <header className="sticky top-0 z-30 border-b border-olive/20 bg-cream/90 backdrop-blur">
      <div className="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 text-walnut">
          <ArchMark className="w-6 h-9" />
          <span className="font-display text-2xl tracking-tight">nypiel</span>
        </Link>

        <nav className="hidden md:flex items-center gap-8">
          {user && (
            <>
              <NavLink to="/scan" className={linkClass}>Scan</NavLink>
              <NavLink to="/history" className={linkClass}>My results</NavLink>
              <NavLink to="/chat" className={linkClass}>Ask nypiel</NavLink>
              <NavLink to="/guide" className={linkClass}>Guide</NavLink>
            </>
          )}
        </nav>

        <div className="flex items-center gap-4">
          {user ? (
            <>
              <span className="hidden sm:block text-sm text-clay">{user.name || user.email}</span>
              <button
                onClick={() => { logout(); navigate('/') }}
                className="text-sm border border-walnut/30 rounded-full px-4 py-1.5 text-walnut hover:bg-walnut hover:text-cream transition-colors"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm text-walnut hover:text-clay">Log in</Link>
              <Link
                to="/signup"
                className="text-sm bg-walnut text-cream rounded-full px-5 py-2 hover:bg-clay transition-colors"
              >
                Get started
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
