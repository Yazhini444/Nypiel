import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ImageCapture from '../components/ImageCapture'
import { api } from '../lib/api'

export default function Scan() {
  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleAnalyze() {
    if (!file) return
    setError('')
    setBusy(true)
    try {
      const result = await api.analyze(file, true)
      navigate('/results', { state: { result } })
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-16 text-center">
      <p className="text-xs tracking-wide text-olive uppercase mb-2">Step 1 of 2</p>
      <h1 className="font-display text-4xl text-walnut mb-3">Let's look at your skin</h1>
      <p className="text-clay text-sm mb-10 max-w-md mx-auto">
        Use natural light, remove makeup if you can, and face the camera directly for the most
        accurate read.
      </p>

      <ImageCapture onImageReady={setFile} />

      {error && <p className="text-sm text-rust mt-6">{error}</p>}

      <button
        onClick={handleAnalyze}
        disabled={!file || busy}
        className="mt-10 bg-walnut text-cream rounded-full px-8 py-3 text-sm hover:bg-clay transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {busy ? 'Analyzing your skin…' : 'Analyze my skin'}
      </button>
    </div>
  )
}
