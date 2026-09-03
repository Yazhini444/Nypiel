import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { concernLabel } from '../components/ConcernOverlay'

export default function History() {
  const [scans, setScans] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.history().then(setScans).catch((err) => setError(err.message))
  }, [])

  async function handleDelete(id) {
    await api.deleteScan(id)
    setScans((prev) => prev.filter((s) => s.id !== id))
  }

  if (error) return <p className="text-center text-rust py-16">{error}</p>
  if (!scans) return <p className="text-center text-clay py-16">Loading your results…</p>

  if (scans.length === 0) {
    return (
      <div className="max-w-lg mx-auto px-6 py-24 text-center">
        <h1 className="font-display text-3xl text-walnut mb-3">No saved results yet</h1>
        <p className="text-clay text-sm mb-8">Run your first scan to start tracking your skin over time.</p>
        <Link to="/scan" className="bg-walnut text-cream rounded-full px-7 py-3 text-sm hover:bg-clay transition-colors">
          Start a scan
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-16">
      <h1 className="font-display text-4xl text-walnut mb-10">My results</h1>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {scans.map((s) => (
          <div key={s.id} className="rounded-3xl overflow-hidden border border-olive/20 bg-white/40 group">
            <Link to={`/results/${s.id}`}>
              <img src={s.image_path} alt="" className="w-full aspect-square object-cover" />
            </Link>
            <div className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-display text-lg text-walnut capitalize">{s.skin_type}</span>
                <span className="text-xs text-clay">
                  {new Date(s.created_at).toLocaleDateString()}
                </span>
              </div>
              <p className="text-xs text-clay leading-relaxed line-clamp-2">
                {s.concerns.map((c) => concernLabel(c.label)).join(', ')}
              </p>
              <div className="flex items-center justify-between mt-3">
                <Link to={`/results/${s.id}`} className="text-xs text-walnut underline underline-offset-4">
                  View details
                </Link>
                <button onClick={() => handleDelete(s.id)} className="text-xs text-rust">
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
