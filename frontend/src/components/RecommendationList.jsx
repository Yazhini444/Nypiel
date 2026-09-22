export default function RecommendationList({ recommendations = [] }) {
  if (!recommendations.length) return null
  return (
    <div>
      <p className="text-xs tracking-wide text-olive uppercase mb-3">Ingredients to look for</p>
      <div className="divide-y divide-olive/15 border-t border-b border-olive/15">
        {recommendations.map((r) => (
          <div key={r.ingredient} className="py-4 flex items-start justify-between gap-6">
            <div>
              <p className="font-display text-lg text-walnut">{r.ingredient}</p>
              <p className="text-sm text-clay mt-0.5 max-w-md">{r.why}</p>
            </div>
            <div className="text-right shrink-0">
              <p className="text-sm text-walnut">{r.use}</p>
              <p className="text-xs text-clay">{r.frequency}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
