import ArchMark from './ArchMark'

export default function Logo({
  variant = 'full', // 'full' (vertical stack), 'horizontal', 'mark-only', 'compact'
  className = '',
  markClass = '',
  theme = 'dark', // 'dark' (walnut/clay text) or 'light' (cream text)
}) {
  const isDark = theme === 'dark'
  const textColor = isDark ? 'text-walnut' : 'text-cream'
  const subColor = isDark ? 'text-clay' : 'text-cream/80'

  if (variant === 'mark-only') {
    return <ArchMark className={markClass || 'w-10 h-14'} />
  }

  if (variant === 'horizontal') {
    return (
      <div className={`flex items-center gap-3 ${className}`}>
        <ArchMark className={markClass || 'w-7 h-10'} />
        <div className="flex flex-col">
          <span className={`font-display text-2xl tracking-tight leading-none ${textColor}`}>
            nypiel
          </span>
          <span className={`text-[9px] tracking-[0.25em] font-medium uppercase mt-0.5 ${subColor}`}>
            Premium Skincare
          </span>
        </div>
      </div>
    )
  }

  if (variant === 'compact') {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <ArchMark className={markClass || 'w-6 h-9'} />
        <span className={`font-display text-2xl tracking-tight ${textColor}`}>nypiel</span>
      </div>
    )
  }

  // Default: 'full' (Vertical lockup matching Image 4)
  return (
    <div className={`flex flex-col items-center text-center ${className}`}>
      <ArchMark className={markClass || 'w-16 h-24'} />
      <h1 className={`font-display text-3xl sm:text-4xl tracking-tight mt-3 leading-none ${textColor}`}>
        nypiel
      </h1>
      <p className={`text-[10px] sm:text-xs tracking-[0.28em] font-medium uppercase mt-2.5 ${subColor}`}>
        Premium Skincare
      </p>
    </div>
  )
}
