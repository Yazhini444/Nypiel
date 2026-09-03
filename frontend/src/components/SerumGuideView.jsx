import { useMemo, useState } from 'react'
import { ACTIVATION_SERUMS, DOS_AND_DONTS } from '../data/activesGuideData'

const ACID_IDS = ['glycolic-acid', 'salicylic-acid', 'azelaic-acid', 'vitamin-c']

const timingLabels = { am: 'AM', pm: 'PM', both: 'AM + PM' }

export default function SerumGuideView({ embedded = false }) {
  const [selectedFilter, setSelectedFilter] = useState('acids')
  const [expandedId, setExpandedId] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')

  const filters = [
    { id: 'acids', label: 'Acids', count: ACID_IDS.length },
    { id: 'all', label: 'All actives', count: ACTIVATION_SERUMS.length },
    { id: 'hydration', label: 'Hydration', count: 2 },
    { id: 'repair', label: 'Repair', count: 2 },
  ]

  const visibleSerums = useMemo(() => {
    const query = searchQuery.trim().toLowerCase()
    return ACTIVATION_SERUMS.filter((serum) => {
      const inFilter = selectedFilter === 'all'
        || (selectedFilter === 'acids' && ACID_IDS.includes(serum.id))
        || (selectedFilter === 'hydration' && ['hyaluronic-acid', 'niacinamide'].includes(serum.id))
        || (selectedFilter === 'repair' && ['retinol', 'centella-asiatica'].includes(serum.id))
      const searchable = [serum.name, serum.tagline, ...serum.bestFor, ...serum.benefits].join(' ').toLowerCase()
      return inFilter && (!query || searchable.includes(query))
    })
  }, [searchQuery, selectedFilter])

  const acidSerums = ACTIVATION_SERUMS.filter((serum) => ACID_IDS.includes(serum.id))

  return (
    <div className="w-full">
      {!embedded && (
        <header className="guide-intro max-w-3xl mb-8 sm:mb-12">
          <p className="text-[10px] uppercase tracking-[0.28em] text-rust font-semibold mb-4">Ingredient edit / 01</p>
          <h1 className="font-display text-[2.7rem] sm:text-6xl leading-[0.94] text-walnut max-w-2xl">
            Acids, made <em className="text-rust">simple.</em>
          </h1>
          <p className="mt-5 text-sm sm:text-base leading-relaxed text-clay max-w-xl">
            A calm, clear guide to what each active does, when to use it, and how often your skin actually needs it.
          </p>
        </header>
      )}

      <section className="bg-walnut text-cream rounded-[2rem] p-5 sm:p-8 mb-8 overflow-hidden relative">
        <div className="absolute -right-10 -top-14 w-40 h-40 rounded-full border border-cream/10" />
        <div className="relative max-w-2xl">
          <p className="text-[10px] uppercase tracking-[0.25em] text-cream/60 mb-3">Start here</p>
          <h2 className="font-display text-2xl sm:text-3xl mb-2">The acid edit</h2>
          <p className="text-sm leading-relaxed text-cream/70 max-w-lg">
            Acids exfoliate, unclog, brighten, or calm. Choose one goal first, then give your skin time to respond.
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-6">
            {acidSerums.map((serum) => (
              <div key={serum.id} className="border border-cream/15 rounded-xl p-3 min-w-0">
                <span className="block text-lg font-display" style={{ color: serum.color }}>●</span>
                <span className="block text-xs font-semibold mt-1 truncate">{serum.shortName.replace(' Acid', '')}</span>
                <span className="block text-[10px] text-cream/55 mt-1">{serum.frequencyBadge}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="flex flex-col sm:flex-row gap-3 justify-between mb-6">
        <div className="flex gap-2 overflow-x-auto scrollbar-none pb-1 -mx-1 px-1">
          {filters.map((filter) => (
            <button
              key={filter.id}
              onClick={() => setSelectedFilter(filter.id)}
              className={`shrink-0 rounded-full border px-4 py-2 text-xs font-semibold transition-colors ${selectedFilter === filter.id ? 'bg-rust border-rust text-white' : 'bg-white/50 border-olive/25 text-clay hover:border-rust/50'}`}
            >
              {filter.label} <span className="opacity-60">{filter.count}</span>
            </button>
          ))}
        </div>
        <label className="relative shrink-0 sm:w-64">
          <span className="sr-only">Search ingredients</span>
          <input
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Search ingredients"
            className="w-full bg-white/60 border border-olive/25 rounded-full px-4 py-2.5 text-xs text-walnut placeholder:text-clay/60 focus:outline-none focus:ring-2 focus:ring-rust/30"
          />
          <span className="absolute right-4 top-2.5 text-clay" aria-hidden="true">⌕</span>
        </label>
      </div>

      <div className="flex items-center justify-between mb-3">
        <h2 className="font-display text-2xl sm:text-3xl text-walnut">What does it do?</h2>
        <span className="text-[10px] uppercase tracking-[0.18em] text-clay">{visibleSerums.length} shown</span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        {visibleSerums.map((serum) => {
          const isExpanded = expandedId === serum.id
          return (
            <article key={serum.id} className="bg-white/70 border border-olive/20 rounded-2xl overflow-hidden shadow-sm">
              <button
                className="w-full text-left p-4 sm:p-5"
                onClick={() => setExpandedId(isExpanded ? null : serum.id)}
                aria-expanded={isExpanded}
              >
                <div className="flex items-start gap-3">
                  <span className="w-10 h-10 rounded-full shrink-0 flex items-center justify-center text-xl" style={{ backgroundColor: serum.bgColor, color: serum.color }}>✦</span>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-[10px] uppercase tracking-[0.16em] font-semibold" style={{ color: serum.color }}>{serum.category}</p>
                        <h3 className="font-display text-xl text-walnut leading-tight mt-1">{serum.shortName}</h3>
                      </div>
                      <span className="text-clay text-lg leading-none">{isExpanded ? '−' : '+'}</span>
                    </div>
                    <p className="text-sm text-walnut/80 mt-2">{serum.tagline}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 mt-4">
                  <div className="bg-cream/80 rounded-xl px-3 py-2">
                    <span className="block text-[9px] uppercase tracking-[0.15em] text-clay">Use</span>
                    <span className="block text-xs font-semibold text-walnut mt-1">{timingLabels[serum.timingType]}</span>
                  </div>
                  <div className="bg-cream/80 rounded-xl px-3 py-2">
                    <span className="block text-[9px] uppercase tracking-[0.15em] text-clay">How often</span>
                    <span className="block text-xs font-semibold text-walnut mt-1">{serum.frequencyBadge}</span>
                  </div>
                </div>
              </button>

              {isExpanded && (
                <div className="border-t border-olive/15 bg-parchment/30 px-4 pb-5 pt-4 sm:px-5">
                  <p className="text-[10px] uppercase tracking-[0.16em] text-clay font-semibold mb-2">What it does</p>
                  <ul className="space-y-2 text-sm text-ink/80">
                    {serum.benefits.map((benefit) => <li key={benefit} className="flex gap-2"><span className="text-rust">•</span><span>{benefit}</span></li>)}
                  </ul>
                  <p className="text-xs text-clay leading-relaxed mt-4 pt-4 border-t border-olive/15"><strong className="text-walnut">How to use:</strong> {serum.howToUse}</p>
                  {serum.avoidPairing.length > 0 && <p className="text-xs text-rust leading-relaxed mt-3"><strong>Keep separate from:</strong> {serum.avoidPairing.join(', ')}</p>}
                </div>
              )}
            </article>
          )
        })}
      </div>

      {visibleSerums.length === 0 && <p className="rounded-2xl border border-dashed border-olive/30 py-12 text-center text-sm text-clay">No ingredients match that search.</p>}

      <section className="mt-12 sm:mt-16 pt-8 border-t border-olive/20">
        <p className="text-[10px] uppercase tracking-[0.25em] text-rust font-semibold mb-3">Keep your barrier happy</p>
        <h2 className="font-display text-2xl sm:text-3xl text-walnut mb-5">The rules worth remembering</h2>
        <div className="grid sm:grid-cols-2 gap-3">
          {DOS_AND_DONTS.map((item, index) => <div key={item.rule} className="bg-white/50 border border-olive/15 rounded-2xl p-4"><span className="text-xs text-rust font-semibold">0{index + 1}</span><h3 className="font-semibold text-sm text-walnut mt-2">{item.rule}</h3><p className="text-xs text-clay leading-relaxed mt-2">{item.desc}</p></div>)}
        </div>
      </section>
    </div>
  )
}
