/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        obsidian: {
          DEFAULT: '#07090E',
          deep: '#040508',
          card: '#0D111A',
          surface: '#131926',
          border: 'rgba(255, 255, 255, 0.08)',
        },
        cyan: {
          neon: '#00F0FF',
          glow: 'rgba(0, 240, 255, 0.4)',
        },
        sapphire: {
          DEFAULT: '#3B82F6',
          bright: '#60A5FA',
          glow: 'rgba(59, 130, 246, 0.4)',
        },
        emerald: {
          phosphor: '#10B981',
          glow: 'rgba(16, 185, 129, 0.4)',
        },
        primary: {
          DEFAULT: '#00F0FF', // Electric Cyan
          dark: '#00B8C4',
          light: '#67F7FF',
        },
        secondary: {
          DEFAULT: '#3B82F6', // Luminous Sapphire
          hover: '#2563EB',
          light: '#93C5FD',
        },
        accent: {
          DEFAULT: '#10B981', // Phosphor Emerald
          hover: '#059669',
          light: '#6EE7B7',
        },
        bg: {
          DEFAULT: '#07090E', // Dark Obsidian Canvas
          card: '#0D111A',
          muted: '#111726',
        },
        fg: {
          DEFAULT: '#F8FAFC', // Slate White
          muted: '#94A3B8',
          subtle: '#64748B',
        },
        border: {
          DEFAULT: 'rgba(255, 255, 255, 0.09)',
          focus: '#00F0FF',
        },
        success: '#10B981',
        destructive: '#EF4444',
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', '"Inter"', 'system-ui', 'sans-serif'],
        heading: ['"Syne"', '"Plus Jakarta Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'glass': '0 20px 50px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08)',
        'cyan-glow': '0 0 25px rgba(0, 240, 255, 0.25), 0 0 50px rgba(0, 240, 255, 0.1)',
        'sapphire-glow': '0 0 25px rgba(59, 130, 246, 0.25), 0 0 50px rgba(59, 130, 246, 0.1)',
        'emerald-glow': '0 0 25px rgba(16, 185, 129, 0.25), 0 0 50px rgba(16, 185, 129, 0.1)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}
