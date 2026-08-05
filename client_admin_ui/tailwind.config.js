/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bgDeep: '#06070f',
        bgBase: '#0a0c18',
        bgElevated: '#0f1221',
        blue: '#3B82F6',
        green: '#10B981',
        amber: '#F59E0B',
        red: '#EF4444',
        violet: '#8B5CF6',
        indigo: '#5E6AD2',
        cyan: '#06B6D4',
        textPrimary: '#EDEDEF',
        textSecondary: '#8A8F98',
        textMuted: '#4A5060',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
