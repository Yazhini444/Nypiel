export default function ArchMark({ className = 'w-10 h-14', color = 'currentColor', leafColor = 'currentColor' }) {
  return (
    <svg
      viewBox="0 0 160 240"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="nypiel botanical arch emblem"
    >
      {/* Arch Outline */}
      <path
        d="M20 185 V 75 C 20 38 48 10 80 10 C 112 10 140 38 140 75 V 185 Z"
        stroke={color}
        strokeWidth="2.2"
        strokeLinejoin="round"
      />

      {/* Main Botanical Central Stem extending below baseline */}
      <line
        x1="80"
        y1="40"
        x2="80"
        y2="215"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
      />

      {/* 4-point Diamond Accent Node at Baseline Intersection */}
      <path
        d="M 80 181 L 83.5 185 L 80 189 L 76.5 185 Z"
        fill={color}
      />

      {/* Botanical Branches & Leaf Sprigs */}
      {/* Lower Left Sprig */}
      <path d="M80 155 Q 68 148 58 138" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
      <path d="M58 138 C 53 132 56 124 64 128 C 67 134 62 140 58 138 Z" fill={leafColor} stroke={color} strokeWidth="1" />
      <path d="M68 148 C 62 144 62 137 70 140 C 73 145 70 150 68 148 Z" fill={leafColor} stroke={color} strokeWidth="1" />
      <path d="M62 130 C 67 122 74 125 72 132 C 68 136 63 134 62 130 Z" fill={leafColor} stroke={color} strokeWidth="1" />

      {/* Mid Left Leaves */}
      <path d="M80 120 Q 69 110 62 98" stroke={color} strokeWidth="1.4" strokeLinecap="round" />
      <path d="M62 98 C 59 90 68 89 71 97 C 71 103 64 105 62 98 Z" fill={leafColor} stroke={color} strokeWidth="1" />
      <path d="M72 110 C 66 104 71 97 76 101 C 78 107 74 112 72 110 Z" fill={leafColor} stroke={color} strokeWidth="1" />

      {/* Lower Right Sprig */}
      <path d="M80 135 Q 92 125 102 110" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
      <path d="M102 110 C 108 105 111 112 105 116 C 98 119 96 113 102 110 Z" fill={leafColor} stroke={color} strokeWidth="1" />
      <path d="M92 124 C 98 118 102 122 97 128 C 92 131 89 127 92 124 Z" fill={leafColor} stroke={color} strokeWidth="1" />
      <path d="M95 114 C 102 108 107 113 100 119 C 96 121 93 118 95 114 Z" fill={leafColor} stroke={color} strokeWidth="1" />

      {/* Upper Right Sprig */}
      <path d="M80 90 Q 90 78 98 67" stroke={color} strokeWidth="1.4" strokeLinecap="round" />
      <path d="M98 67 C 104 60 107 67 101 72 C 96 75 94 70 98 67 Z" fill={leafColor} stroke={color} strokeWidth="1" />
      <path d="M88 81 C 95 75 99 80 94 85 C 89 88 86 84 88 81 Z" fill={leafColor} stroke={color} strokeWidth="1" />

      {/* Upper Left Sprig */}
      <path d="M80 95 Q 72 85 70 74" stroke={color} strokeWidth="1.4" strokeLinecap="round" />
      <path d="M70 74 C 67 66 74 65 77 74 C 77 79 71 81 70 74 Z" fill={leafColor} stroke={color} strokeWidth="1" />

      {/* Apex Buds */}
      <path d="M80 60 Q 84 48 85 40" stroke={color} strokeWidth="1.2" strokeLinecap="round" />
      <path d="M85 40 C 87 32 92 34 89 42 C 87 46 83 45 85 40 Z" fill={leafColor} stroke={color} strokeWidth="1" />
      <path d="M77 48 C 73 42 79 39 82 46 C 83 50 78 51 77 48 Z" fill={leafColor} stroke={color} strokeWidth="1" />
    </svg>
  )
}
