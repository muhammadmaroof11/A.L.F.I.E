/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        clientBg: '#05060A',
        clientSurface: '#12141F',
        clientPrimary: '#6366f1',
        clientText: '#f8fafc',
        clientMuted: '#94a3b8'
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
