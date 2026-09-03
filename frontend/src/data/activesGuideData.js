export const ACTIVATION_SERUMS = [
  {
    id: 'retinol',
    name: 'Retinol (Vitamin A)',
    shortName: 'Retinol',
    tagline: 'Renew & Smooth',
    category: 'Exfoliant & Renewal',
    color: '#8B5CF6',
    bgColor: '#F5F3FF',
    borderColor: '#DDD6FE',
    timing: 'Night Only',
    timingType: 'pm', // 'am', 'pm', 'both'
    frequency: '1–3 Times Per Week',
    frequencyBadge: '1-3x / week',
    benefits: [
      'Speeds up cellular turnover',
      'Softens fine lines & wrinkles',
      'Stimulates collagen production',
      'Improves overall skin texture'
    ],
    bestFor: ['Wrinkles & Fine Lines', 'Uneven Texture', 'Loss of Firmness', 'Dullness'],
    howToUse: 'Apply 2–3 drops on clean, completely dry skin at night. Start 1x/week and slowly build tolerance. Always follow with moisturizer and use broad-spectrum SPF 30+ every morning.',
    pairsWellWith: ['Hyaluronic Acid', 'Niacinamide', 'Ceramides', 'Centella Asiatica'],
    avoidPairing: ['Direct Glycolic Acid (AHA)', 'Salicylic Acid (BHA)', 'High-Strength L-Ascorbic Acid (same routine)']
  },
  {
    id: 'glycolic-acid',
    name: 'Glycolic Acid (AHA)',
    shortName: 'Glycolic Acid',
    tagline: 'Exfoliate & Brighten',
    category: 'Exfoliant & Renewal',
    color: '#0D9488',
    bgColor: '#F0FDFA',
    borderColor: '#CCFBF1',
    timing: 'Night Only',
    timingType: 'pm',
    frequency: '1–3 Times Per Week',
    frequencyBadge: '1-3x / week',
    benefits: [
      'Gently dissolves dead surface skin cells',
      'Brightens dull, lacklustre complexion',
      'Smooths rough, bumpy skin texture',
      'Fades surface hyperpigmentation'
    ],
    bestFor: ['Dull Skin', 'Rough Texture', 'Sun Damage', 'Uneven Tone'],
    howToUse: 'Apply 2–3 drops after cleansing at night. Let absorb before layering hydrating serums. Do not apply on broken or irritated skin.',
    pairsWellWith: ['Hyaluronic Acid', 'Centella Asiatica', 'Ceramides'],
    avoidPairing: ['Retinol', 'Salicylic Acid', 'Physical Scrubs']
  },
  {
    id: 'salicylic-acid',
    name: 'Salicylic Acid (BHA)',
    shortName: 'Salicylic Acid',
    tagline: 'Clear & Unclog',
    category: 'Clarifying & Pores',
    color: '#16A34A',
    bgColor: '#F0FDF4',
    borderColor: '#DCFCE7',
    timing: 'Night Preferred',
    timingType: 'pm',
    frequency: '1–3 Times Per Week',
    frequencyBadge: '1-3x / week',
    benefits: [
      'Penetrates deep inside pores to melt oil',
      'Clears active acne, blackheads & whiteheads',
      'Regulates excess sebum production',
      'Reduces inflammatory blemish swelling'
    ],
    bestFor: ['Acne & Breakouts', 'Blackheads', 'Enlarged Pores', 'Oily Skin'],
    howToUse: 'Apply 2–3 drops focused on the T-zone or congested areas. Can be used as a targeted spot treatment or all-over serum.',
    pairsWellWith: ['Niacinamide', 'Hyaluronic Acid', 'Centella Asiatica', 'Zinc PCA'],
    avoidPairing: ['Retinol', 'Glycolic Acid', 'Harsh Scrubs']
  },
  {
    id: 'azelaic-acid',
    name: 'Azelaic Acid',
    shortName: 'Azelaic Acid',
    tagline: 'Calm & Even Tone',
    category: 'Brightening & Calming',
    color: '#E11D48',
    bgColor: '#FFF1F2',
    borderColor: '#FFE4E6',
    timing: 'Morning or Evening',
    timingType: 'both',
    frequency: 'Once Daily',
    frequencyBadge: 'Once Daily',
    benefits: [
      'Significantly reduces skin redness & rosacea',
      'Fades post-acne marks (PIE & PIH)',
      'Gently clears pore blockages',
      'Evens out blotchy, sensitive skin tone'
    ],
    bestFor: ['Redness & Rosacea', 'Post-Acne Marks', 'Uneven Tone', 'Sensitive Blemishes'],
    howToUse: 'Apply a pea-sized amount or 2–3 drops morning or night. Exceptionally well-tolerated by sensitive and reactive skin.',
    pairsWellWith: ['Niacinamide', 'Hyaluronic Acid', 'Centella Asiatica', 'Vitamin C'],
    avoidPairing: []
  },
  {
    id: 'vitamin-c',
    name: 'Vitamin C (L-Ascorbic Acid)',
    shortName: 'Vitamin C',
    tagline: 'Brighten & Protect',
    category: 'Brightening & Antioxidant',
    color: '#D97706',
    bgColor: '#FFFBEB',
    borderColor: '#FEF3C7',
    timing: 'Morning (Recommended)',
    timingType: 'am',
    frequency: 'Once Daily (or 3–4x/week)',
    frequencyBadge: 'Once Daily',
    benefits: [
      'Brightens skin radiance and glow',
      'Fades stubborn dark spots & sun damage',
      'Neutralizes environmental free radicals',
      'Boosts natural collagen synthesis'
    ],
    bestFor: ['Dark Spots', 'Dullness', 'Uneven Tone', 'Daily Environmental Protection'],
    howToUse: 'Apply 2–3 drops in the morning on clean, dry skin. Follow with moisturizer and always finish with sunscreen to maximize photoprotection.',
    pairsWellWith: ['Vitamin E', 'Ferulic Acid', 'Hyaluronic Acid', 'Sunscreen'],
    avoidPairing: ['Retinol (use Retinol PM, Vitamin C AM)', 'Direct AHAs/BHAs simultaneously']
  },
  {
    id: 'hyaluronic-acid',
    name: 'Hyaluronic Acid',
    shortName: 'Hyaluronic Acid',
    tagline: 'Hydrate & Plump',
    category: 'Hydration & Barrier',
    color: '#0284C7',
    bgColor: '#F0F9FF',
    borderColor: '#E0F2FE',
    timing: 'Morning & Night',
    timingType: 'both',
    frequency: '1–2 Times Daily',
    frequencyBadge: 'Daily (AM & PM)',
    benefits: [
      'Binds up to 1,000x its weight in water',
      'Intensely hydrates and plumps skin',
      'Smooths dehydration fine lines',
      'Fortifies skin moisture barrier'
    ],
    bestFor: ['Dehydration', 'Dry Skin', 'Dullness', 'All Skin Types'],
    howToUse: 'Apply 2–3 drops onto slightly damp skin immediately after cleansing/toning. Lock in with moisturizer so moisture cannot evaporate.',
    pairsWellWith: ['All skincare ingredients — universally compatible!'],
    avoidPairing: []
  },
  {
    id: 'niacinamide',
    name: 'Niacinamide (Vitamin B3)',
    shortName: 'Niacinamide',
    tagline: 'Balance & Strengthen',
    category: 'Barrier & Balance',
    color: '#059669',
    bgColor: '#ECFDF5',
    borderColor: '#D1FAE5',
    timing: 'Morning & Night',
    timingType: 'both',
    frequency: '1–2 Times Daily',
    frequencyBadge: '1-2x Daily',
    benefits: [
      'Visibly minimizes enlarged pores',
      'Regulates and balances excess oil',
      'Strengthens the skin lipid barrier',
      'Soothes redness and improves skin texture'
    ],
    bestFor: ['Large Pores', 'Excess Sebum', 'Weakened Barrier', 'Blemish Prone Skin'],
    howToUse: 'Apply 2–3 drops morning and evening before thicker creams. Works seamlessly with almost all skincare actives.',
    pairsWellWith: ['Hyaluronic Acid', 'Salicylic Acid', 'Peptides', 'Zinc PCA', 'Azelaic Acid'],
    avoidPairing: []
  },
  {
    id: 'arbutin',
    name: 'Alpha Arbutin',
    shortName: 'Alpha Arbutin',
    tagline: 'Brighten & Fade Spots',
    category: 'Brightening & Tone',
    color: '#DB2777',
    bgColor: '#FDF2F8',
    borderColor: '#FCE7F3',
    timing: 'Morning or Evening',
    timingType: 'both',
    frequency: '1–2 Times Daily',
    frequencyBadge: '1-2x Daily',
    benefits: [
      'Inhibits tyrosinase to stop pigment synthesis',
      'Fades dark spots, sun spots & melasma',
      'Safe, gentle alternative for sensitive pigment',
      'Promotes an even, luminous complexion'
    ],
    bestFor: ['Hyperpigmentation', 'Dark Spots', 'Post-Blemish Discoloration', 'Melasma'],
    howToUse: 'Apply 2–3 drops all over the face or targeted to areas with stubborn pigmentation. Always wear SPF during the day.',
    pairsWellWith: ['Vitamin C', 'Niacinamide', 'Hyaluronic Acid'],
    avoidPairing: []
  },
  {
    id: 'peptides',
    name: 'Peptides (Signal & Matrixyl)',
    shortName: 'Peptides',
    tagline: 'Firm & Repair',
    category: 'Anti-Aging & Firming',
    color: '#7C3AED',
    bgColor: '#F5F3FF',
    borderColor: '#EDE9FE',
    timing: 'Morning or Evening',
    timingType: 'both',
    frequency: '1–2 Times Daily',
    frequencyBadge: '1-2x Daily',
    benefits: [
      'Signals fibroblasts to rebuild collagen',
      'Firms and improves skin elasticity',
      'Smooths under-eye skin and fine lines',
      'Supports deep skin repair and resilience'
    ],
    bestFor: ['Loss of Elasticity', 'Fine Lines & Wrinkles', 'Under-Eye Area', 'Mature Skin'],
    howToUse: 'Apply 2–3 drops morning and night. Excellent for face, neck, and delicate eye contour areas.',
    pairsWellWith: ['Hyaluronic Acid', 'Niacinamide', 'Ceramides', 'Vitamin C'],
    avoidPairing: ['Direct strong acids (like high Glycolic Acid) at exact same instant if using Copper Peptides']
  },
  {
    id: 'centella-asiatica',
    name: 'Centella Asiatica (Cica)',
    shortName: 'Centella Asiatica',
    tagline: 'Soothe & Heal',
    category: 'Soothing & Repair',
    color: '#65A30D',
    bgColor: '#F7FEE7',
    borderColor: '#ECFCCB',
    timing: 'Morning & Night',
    timingType: 'both',
    frequency: '1–2 Times Daily',
    frequencyBadge: '1-2x Daily',
    benefits: [
      'Calms acute redness and skin irritation',
      'Speeds up compromised barrier recovery',
      'Delivers deep antioxidant protection',
      'Soothes post-treatment or exfoliated skin'
    ],
    bestFor: ['Irritation & Redness', 'Compromised Skin Barrier', 'Sensitive Skin', 'Post-Breakout Healing'],
    howToUse: 'Apply 2–3 drops whenever skin feels tight, reactive, or flushed. Can be used AM and PM generously.',
    pairsWellWith: ['Retinol (reduces purging/irritation)', 'Salicylic Acid', 'Hyaluronic Acid', 'Ceramides'],
    avoidPairing: []
  }
]

export const DOS_AND_DONTS = [
  {
    rule: 'The "2–3 Drops" Golden Rule',
    desc: 'Serums are potent concentrates. 2 to 3 drops is the optimal dosage for the entire face. Using more does not increase efficacy and can cause irritation or product pilling.'
  },
  {
    rule: 'Consistency: Thinnest to Thickest',
    desc: 'Always apply watery humectants (Hyaluronic Acid) first, followed by active serums (Niacinamide, Vitamin C, Retinol), and seal with moisturizer/facial oil.'
  },
  {
    rule: 'Photosensitivity & Night Actives',
    desc: 'Retinol, Glycolic Acid, and Salicylic Acid increase your skin’s vulnerability to UV damage. Always reserve them for PM routines and wear daily broad-spectrum SPF 30+.'
  },
  {
    rule: 'Active Cycling (Skin Cycling)',
    desc: 'Avoid using Retinol and strong chemical exfoliants (Glycolic / Salicylic Acid) in the exact same evening routine. Alternate nights (e.g., Night 1: Exfoliate, Night 2: Retinoid, Nights 3-4: Recovery/Hydration).'
  }
]
