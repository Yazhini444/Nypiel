import { useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { api } from '../lib/api'

export default function Chat() {
  const location = useLocation()
  const scanId = location.state?.scanId
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      text: scanId
        ? "I've got your latest scan open — ask me anything about your skin type, concerns, or the ingredients I suggested."
        : "Ask me anything about skin types, concerns, or ingredients like retinol, niacinamide, or vitamin C.",
    },
  ])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function send(e) {
    e.preventDefault()
    const text = input.trim()
    if (!text || busy) return
    setMessages((m) => [...m, { role: 'user', text }])
    setInput('')
    setBusy(true)
    try {
      const { reply } = await api.ask(text, scanId)
      setMessages((m) => [...m, { role: 'bot', text: reply }])
    } catch (err) {
      setMessages((m) => [...m, { role: 'bot', text: `Sorry — ${err.message}` }])
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-12 flex flex-col h-[calc(100vh-5rem)]">
      <h1 className="font-display text-3xl text-walnut mb-1">Ask nypiel</h1>
      <p className="text-sm text-clay mb-6">Questions about skin types, concerns, and ingredients.</p>

      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                m.role === 'user'
                  ? 'bg-walnut text-cream rounded-br-sm'
                  : 'bg-white/60 border border-olive/20 text-ink rounded-bl-sm'
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}
        {busy && <p className="text-xs text-clay">nypiel is thinking…</p>}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={send} className="flex items-center gap-3 mt-6 border-t border-olive/20 pt-5">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about retinol, dark spots, your last scan…"
          className="flex-1 border border-olive/30 rounded-full px-5 py-2.5 bg-white/60 focus:border-walnut outline-none text-sm"
        />
        <button
          type="submit"
          disabled={busy}
          className="bg-walnut text-cream rounded-full px-5 py-2.5 text-sm hover:bg-clay transition-colors disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  )
}
