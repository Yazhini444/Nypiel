import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-6">
      <h1 className="font-display text-4xl text-walnut mb-3">Page not found</h1>
      <p className="text-clay mb-8">The page you're looking for doesn't exist.</p>
      <Link to="/" className="text-sm text-walnut underline underline-offset-4">Back to home</Link>
    </div>
  )
}
