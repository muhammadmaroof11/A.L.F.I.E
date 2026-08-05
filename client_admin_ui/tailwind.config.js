/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#070a0f',
        surface: 'rgba(255, 255, 255, 0.03)',
        surfaceHover: 'rgba(255, 255, 255, 0.06)',
        border: 'rgba(255, 255, 255, 0.08)',
        borderHover: 'rgba(255, 255, 255, 0.15)',
        textPrimary: '#f0f4f8',
        textSecondary: 'rgba(240, 244, 248, 0.65)',
        textMuted: 'rgba(240, 244, 248, 0.4)',
        accent: '#14b8a6', // Teal
        accentGlow: 'rgba(20, 184, 166, 0.3)',
        accentSecondary: '#10b981', // Emerald
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
        'glass-elevated': '0 20px 60px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1)',
        'glow': '0 0 30px rgba(20, 184, 166, 0.4), 0 4px 20px rgba(0, 0, 0, 0.3)',
      },
      backgroundImage: {
        'gradient-accent': 'linear-gradient(135deg, #14b8a6 0%, #10b981 100%)',
      }
    },
  },
  plugins: [],
}
