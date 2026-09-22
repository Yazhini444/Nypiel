import { useEffect, useState } from 'react'
import { useLocation, useParams, Link } from 'react-router-dom'
import ConcernOverlay, { concernLabel } from '../components/ConcernOverlay'
import SkinTypeBadge from '../components/SkinTypeBadge'
import RecommendationList from '../components/RecommendationList'
import { api } from '../lib/api'

export default function Results() {
  const location = useLocation()
  const { id } = useParams()
  const [result, setResult] = useState(location.state?.result || null)
  const [activeLabel, setActiveLabel] = useState(null)
  const [loading, setLoading] = useState(!location.state?.result)
  const [error, setError] = useState('')

  useEffect(() => {
    if (result || !id) return
    api
      .getScan(id)
      .then(setResult)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [id, result])

  if (loading) {
    return <div className="min-h-[50vh] flex items-center justify-center text-clay">Loading your results…</div>
  }

  if (error || !result) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center text-center px-6">
        <p className="text-clay mb-4">{error || "We couldn't find that result."}</p>
        <Link to="/scan" className="text-walnut underline underline-offset-4 text-sm">Start a new scan</Link>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-16">
      <p className="text-xs tracking-wide text-olive uppercase mb-2 text-center">Step 2 of 2</p>
      <h1 className="font-display text-4xl text-walnut mb-10 text-center">Here's what we found</h1>

      <div className="grid md:grid-cols-2 gap-12 items-start">
        <div>
          <ConcernOverlay
            imageUrl={result.image_path}
            concerns={result.concerns}
            activeLabel={activeLabel}
          />
          <div className="flex flex-wrap gap-2 mt-4 justify-center">
            {result.concerns.map((c) => (
              <button
                key={c.label}
                onMouseEnter={() => setActiveLabel(c.label)}
                onMouseLeave={() => setActiveLabel(null)}
                className="text-xs border border-olive/30 rounded-full px-3 py-1.5 text-walnut bg-white/50"
              >
                {concernLabel(c.label)} · {Math.round(c.confidence * 100)}%
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-10">
          <SkinTypeBadge type={result.skin_type} confidence={result.skin_type_confidence} />
          <RecommendationList recommendations={result.recommendations} />

          <div className="flex flex-wrap gap-3 pt-2">
            <Link
              to="/chat"
              state={{ scanId: result.id }}
              className="text-sm bg-walnut text-cream rounded-full px-6 py-2.5 hover:bg-clay transition-colors"
            >
              Ask about this result
            </Link>
            <Link
              to="/scan"
              className="text-sm border border-walnut/30 rounded-full px-6 py-2.5 text-walnut hover:bg-walnut hover:text-cream transition-colors"
            >
              New scan
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
