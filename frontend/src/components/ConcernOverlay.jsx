const LABELS = {
  acne: 'Acne',
  dark_spots: 'Dark spots',
  wrinkles: 'Wrinkles',
  redness: 'Redness',
  large_pores: 'Large pores',
  dark_circles: 'Dark circles',
  blackheads: 'Blackheads',
  uneven_texture: 'Uneven texture',
  dehydration: 'Dehydration',
  dullness: 'Dullness',
}

export function concernLabel(key) {
  return LABELS[key] || key.replace(/_/g, ' ')
}

export default function ConcernOverlay({ imageUrl, concerns = [], activeLabel }) {
  return (
    <div className="relative rounded-[28px] overflow-hidden shadow-soft bg-walnut">
      <img src={imageUrl} alt="Analyzed photo" className="w-full h-full object-cover block" />
      {concerns.map((c, i) => {
        if (!c.box) return null
        const [x, y, w, h] = c.box
        const isActive = activeLabel === c.label
        return (
          <div
            key={`${c.label}-${i}`}
            className="absolute transition-all duration-200"
            style={{
              left: `${x * 100}%`,
              top: `${y * 100}%`,
              width: `${w * 100}%`,
              height: `${h * 100}%`,
            }}
          >
            <div
              className={`w-full h-full rounded-full border-2 ${
                isActive ? 'border-rust' : 'border-cream/80'
              }`}
              style={{ boxShadow: isActive ? '0 0 0 4px rgba(176,83,46,0.25)' : 'none' }}
            />
            <span
              className={`absolute -top-6 left-0 text-[11px] px-2 py-0.5 rounded-full whitespace-nowrap ${
                isActive ? 'bg-rust text-cream' : 'bg-cream/90 text-walnut'
              }`}
            >
              {concernLabel(c.label)}
            </span>
          </div>
        )
      })}
    </div>
  )
}
