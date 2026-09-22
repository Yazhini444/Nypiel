/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        cream: '#F3EDE2',
        parchment: '#EAE1D0',
        walnut: '#4A3A28',
        clay: '#8B6F4E',
        olive: '#A9915E',
        sage: '#7C8A6E',
        ink: '#2B2420',
        rust: '#B0532E',
      },
      fontFamily: {
        display: ['"Fraunces"', 'serif'],
        body: ['"Inter"', 'sans-serif'],
      },
      borderRadius: {
        arch: '999px 999px 12px 12px',
      },
      boxShadow: {
        soft: '0 12px 40px -16px rgba(74, 58, 40, 0.35)',
      },
    },
  },
  plugins: [],
}
