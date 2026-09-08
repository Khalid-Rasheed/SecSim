/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        // Light theme tokens (same names kept for compatibility)
        ink: '#f3f6fb', // page background
        panel: '#ffffff', // cards
        panel2: '#edf1f7', // inset / muted surfaces
        mist: '#0f172a', // primary text
        muted: '#64748b', // secondary text
        cipher: '#0d9488', // primary teal (dark enough for light bg)
        keyamber: '#d97706',
        dangerx: '#dc2626'
      },
      fontFamily: {
        display: ['Tajawal', 'sans-serif'],
        sans: ['Tajawal', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace']
      },
      boxShadow: {
        card: '0 1px 2px rgba(15, 23, 42, 0.05), 0 8px 24px -12px rgba(15, 23, 42, 0.18)',
        pop: '0 12px 32px -12px rgba(13, 148, 136, 0.35)'
      }
    }
  },
  plugins: []
}
