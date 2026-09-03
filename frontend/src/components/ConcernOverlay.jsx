const LABELS = {
  acne: 'Acne',
  blackheads: 'Blackheads',
  whiteheads: 'Whiteheads',
  dark_spots: 'Dark Spots',
  dry_skin: 'Dry Skin',
  oily_skin: 'Oily Skin',
  large_pores: 'Enlarged Pores',
  enlarged_pores: 'Enlarged Pores',
  englarged_pores: 'Enlarged Pores',
  eyebags: 'Eye Bags',
  dark_circles: 'Dark Circles',
  redness: 'Redness',
  skin_redness: 'Redness',
  wrinkles: 'Wrinkles',
  uneven_texture: 'Uneven Texture',
  dehydration: 'Dehydration',
  dullness: 'Dullness',
}

export function concernLabel(key) {
  if (!key) return ''
  const norm = key.toLowerCase().replace(/[- ]/g, '_')
  if (LABELS[norm]) return LABELS[norm]
  return key.replace(/[-_]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
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
