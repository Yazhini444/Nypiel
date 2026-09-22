import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import ArchMark from '../components/ArchMark'

const STEPS = [
  { title: 'Scan', desc: 'Upload a photo or use your camera for a live, makeup-free scan.' },
  { title: 'Understand', desc: 'Two models read your skin — one for type, one for specific concerns.' },
  { title: 'Treat', desc: 'Get ingredients matched to what your skin actually needs, not a generic routine.' },
]

const CONCERNS = ['Acne', 'Dark spots', 'Wrinkles', 'Redness', 'Large pores', 'Dark circles', 'Blackheads', 'Uneven texture', 'Dehydration', 'Dullness']

export default function Landing() {
  const { user } = useAuth()

  return (
    <div>
      {/* Hero */}
      <section className="max-w-4xl mx-auto px-6 pt-20 pb-24 text-center">
        <div className="flex justify-center text-olive mb-6">
          <ArchMark className="w-12 h-16" />
        </div>
        <h1 className="font-display text-5xl sm:text-6xl text-walnut leading-[1.08] tracking-tight">
          Skin, but better.
        </h1>
        <p className="mt-6 text-lg text-clay max-w-xl mx-auto leading-relaxed">
          nypiel reads your skin the way a dermatologist would — your type, your specific
          concerns, and exactly which ingredients help. In under a minute.
        </p>
        <div className="mt-10 flex items-center justify-center gap-4">
          <Link
            to={user ? '/scan' : '/signup'}
            className="bg-walnut text-cream rounded-full px-7 py-3 text-sm hover:bg-clay transition-colors"
          >
            Start your scan
          </Link>
          <Link to="/chat" className="text-sm text-walnut underline underline-offset-4">
            Ask a question first
          </Link>
        </div>
      </section>

      {/* Steps */}
      <section className="border-t border-olive/20 bg-parchment/60">
        <div className="max-w-5xl mx-auto px-6 py-20 grid sm:grid-cols-3 gap-12">
          {STEPS.map((s, i) => (
            <div key={s.title} className="text-center sm:text-left">
              <p className="font-display text-4xl text-olive/70 mb-3">{i + 1}</p>
              <h3 className="font-display text-xl text-walnut mb-2">{s.title}</h3>
              <p className="text-sm text-clay leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* What it detects */}
      <section className="max-w-5xl mx-auto px-6 py-24">
        <div className="text-center max-w-lg mx-auto mb-12">
          <h2 className="font-display text-3xl text-walnut">Ten concerns, one scan</h2>
          <p className="text-clay mt-3 text-sm leading-relaxed">
            Our concern model was trained to recognize the details that actually change a
            routine — not just skin type.
          </p>
        </div>
        <div className="flex flex-wrap justify-center gap-3">
          {CONCERNS.map((c) => (
            <span
              key={c}
              className="text-sm text-walnut border border-olive/30 rounded-full px-4 py-2 bg-white/50"
            >
              {c}
            </span>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-olive/20">
        <div className="max-w-3xl mx-auto px-6 py-20 text-center">
          <h2 className="font-display text-3xl text-walnut mb-4">
            Your skin changes. Your routine should too.
          </h2>
          <p className="text-clay text-sm mb-8">
            Save every scan and watch your skin's story unfold over time.
          </p>
          <Link
            to={user ? '/scan' : '/signup'}
            className="inline-block bg-walnut text-cream rounded-full px-7 py-3 text-sm hover:bg-clay transition-colors"
          >
            {user ? 'New scan' : 'Create your free account'}
          </Link>
        </div>
      </section>
    </div>
  )
}
