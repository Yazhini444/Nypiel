import { useRef, useState, useCallback } from 'react'

export default function ImageCapture({ onImageReady }) {
  const [preview, setPreview] = useState(null)
  const [mode, setMode] = useState('idle') // idle | camera
  const [dragOver, setDragOver] = useState(false)
  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const fileInputRef = useRef(null)

  const handleFile = useCallback(
    (file) => {
      if (!file || !file.type.startsWith('image/')) return
      setPreview(URL.createObjectURL(file))
      onImageReady(file)
    },
    [onImageReady],
  )

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
      streamRef.current = stream
      setMode('camera')
      requestAnimationFrame(() => {
        if (videoRef.current) videoRef.current.srcObject = stream
      })
    } catch {
      alert('Could not access the camera. You can upload a photo instead.')
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach((t) => t.stop())
    setMode('idle')
  }

  function capture() {
    const video = videoRef.current
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0)
    canvas.toBlob((blob) => {
      const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' })
      handleFile(file)
      stopCamera()
    }, 'image/jpeg', 0.92)
  }

  if (mode === 'camera') {
    return (
      <div className="relative rounded-[32px] overflow-hidden bg-walnut aspect-[4/5] max-w-md mx-auto shadow-soft">
        <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
        <div className="absolute inset-0 border-[6px] border-cream/20 rounded-[32px] pointer-events-none" />
        <div className="absolute bottom-0 inset-x-0 flex items-center justify-center gap-6 pb-6">
          <button
            onClick={stopCamera}
            className="text-cream/80 text-sm underline underline-offset-4"
          >
            Cancel
          </button>
          <button
            onClick={capture}
            className="w-16 h-16 rounded-full bg-cream border-4 border-olive/60 hover:scale-105 transition-transform"
            aria-label="Capture photo"
          />
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-md mx-auto">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          handleFile(e.dataTransfer.files?.[0])
        }}
        className={`relative rounded-[32px] aspect-[4/5] flex flex-col items-center justify-center text-center px-8 border-2 border-dashed transition-colors ${
          dragOver ? 'border-olive bg-parchment' : 'border-olive/40 bg-white/40'
        } ${preview ? 'border-solid border-olive/0' : ''}`}
      >
        {preview ? (
          <img src={preview} alt="Your uploaded photo" className="w-full h-full object-cover rounded-[30px]" />
        ) : (
          <>
            <div className="w-14 h-14 rounded-full border border-olive/50 flex items-center justify-center mb-5 text-olive">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M4 7h3l2-2h6l2 2h3v12H4V7z" strokeLinejoin="round" />
                <circle cx="12" cy="13" r="3.5" />
              </svg>
            </div>
            <p className="font-display text-lg text-walnut mb-1">Show us your skin</p>
            <p className="text-sm text-clay mb-6">Drag a clear, makeup-free photo here, or choose an option below</p>
          </>
        )}

        {preview && (
          <button
            onClick={() => { setPreview(null); onImageReady(null) }}
            className="absolute top-4 right-4 w-8 h-8 rounded-full bg-walnut/80 text-cream text-sm flex items-center justify-center"
            aria-label="Remove photo"
          >
            ✕
          </button>
        )}
      </div>

      {!preview && (
        <div className="flex items-center justify-center gap-3 mt-5">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="text-sm border border-walnut/30 rounded-full px-5 py-2.5 text-walnut hover:bg-walnut hover:text-cream transition-colors"
          >
            Upload a photo
          </button>
          <button
            onClick={startCamera}
            className="text-sm bg-walnut text-cream rounded-full px-5 py-2.5 hover:bg-clay transition-colors"
          >
            Use live camera
          </button>
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        accept="image/png, image/jpeg, image/webp"
        className="hidden"
        onChange={(e) => handleFile(e.target.files?.[0])}
      />
    </div>
  )
}
