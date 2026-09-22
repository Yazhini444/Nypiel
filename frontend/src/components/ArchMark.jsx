export default function ArchMark({ className = 'w-10 h-14' }) {
  return (
    <svg viewBox="0 0 100 140" className={className} fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M8 132V58C8 30 26 8 50 8C74 8 92 30 92 58V132"
        stroke="currentColor"
        strokeWidth="2.5"
      />
      <path d="M50 34V108" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <path d="M50 44 L38 54 M50 58 L64 66 M50 74 L40 82" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <circle cx="50" cy="118" r="2.2" fill="currentColor" />
    </svg>
  )
}
