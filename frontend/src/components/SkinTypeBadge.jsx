const COPY = {
  dry: { title: 'Dry', desc: 'Produces less natural oil and can feel tight or flaky.' },
  oily: { title: 'Oily', desc: 'Produces more sebum than average, often with visible shine.' },
  combination: { title: 'Combination', desc: 'Oilier through the T-zone, drier on the cheeks.' },
  normal: { title: 'Normal', desc: 'Well-balanced — not too oily and not too dry.' },
}

export default function SkinTypeBadge({ type, confidence }) {
  const copy = COPY[type] || { title: type, desc: '' }
  return (
    <div className="flex items-start gap-4">
      <div className="shrink-0 w-14 h-14 rounded-full bg-parchment border border-olive/40 flex items-center justify-center">
        <span className="font-display text-lg text-walnut">{Math.round(confidence * 100)}%</span>
      </div>
      <div>
        <p className="text-xs tracking-wide text-olive uppercase mb-1">Your skin type</p>
        <h3 className="font-display text-2xl text-walnut leading-tight">{copy.title}</h3>
        <p className="text-sm text-clay mt-1 max-w-xs">{copy.desc}</p>
      </div>
    </div>
  )
}
