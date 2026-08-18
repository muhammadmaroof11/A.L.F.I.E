/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1E3A5F', // Academic Navy
          dark: '#132640',
          light: '#2D568A',
        },
        secondary: {
          DEFAULT: '#2563EB', // Vivid Blue
          hover: '#1D4ED8',
          light: '#DBEAFE',
        },
        accent: {
          DEFAULT: '#A16207', // Warm Gold
          hover: '#854D0E',
          light: '#FEF3C7',
        },
        bg: {
          DEFAULT: '#F8FAFC', // Off-White Canvas
          card: '#FFFFFF',
          muted: '#F1F5F9',
        },
        fg: {
          DEFAULT: '#0F172A', // Near-Black
          muted: '#64748B',
          subtle: '#94A3B8',
        },
        border: {
          DEFAULT: '#E2E8F0',
          focus: '#1E3A5F',
        },
        success: '#059669',
        destructive: '#DC2626',
        niche: {
          law: '#92400E',
          realestate: '#1E40AF',
          carrental: '#065F46',
          clinic: '#0369A1',
          hospitality: '#7C3AED',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(30, 58, 95, 0.08)',
        'glass-hover': '0 16px 48px 0 rgba(30, 58, 95, 0.14)',
        'elevation': '0 4px 20px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.04)',
        'elevation-high': '0 20px 40px -4px rgba(15, 23, 42, 0.1), 0 8px 16px -4px rgba(15, 23, 42, 0.06)',
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
