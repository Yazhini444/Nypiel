import SerumGuideView from '../components/SerumGuideView'
import { Link } from 'react-router-dom'
import Logo from '../components/Logo'

export default function Guide() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-12">
      <div className="flex items-center justify-between mb-8 sm:mb-12">
        <Logo variant="horizontal" markClass="w-7 h-10 sm:w-8 sm:h-12" />
        <span className="text-[10px] uppercase tracking-[0.22em] text-clay">Skin library / 01</span>
      </div>

      <SerumGuideView />

      <div className="mt-12 sm:mt-16 bg-walnut text-cream rounded-[2rem] p-6 sm:p-10 text-center shadow-soft">
        <p className="text-[10px] uppercase tracking-[0.24em] text-cream/60 mb-3">Your next step</p>
        <h3 className="font-display text-2xl sm:text-3xl mb-2">
          Want a routine customized to your exact skin?
        </h3>
        <p className="text-cream/70 text-sm max-w-md mx-auto mb-6">
          Scan your face with nypiel's AI models to diagnose your skin type and detect specific concerns in seconds.
        </p>
        <Link
          to="/scan"
          className="inline-flex items-center gap-2 bg-cream text-walnut rounded-full px-7 py-3 text-sm font-semibold hover:bg-parchment transition-all"
        >
          <span>Start free skin scan</span>
          <span aria-hidden="true">↗</span>
        </Link>
      </div>
    </div>
  )
}
