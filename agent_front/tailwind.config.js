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
          DEFAULT: '#0f172a',
          light: '#1e293b',
        },
        secondary: {
          DEFAULT: '#1e293b',
          light: '#334155',
        },
        accent: {
          DEFAULT: '#14b8a6',
          light: '#2dd4bf',
        },
        userBubble: '#3b82f6',
        aiBubble: '#334155',
      },
      animation: {
        'fadeIn': 'fadeIn 0.3s ease-out',
        'bounce': 'bounce 1.3s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        bounce: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        }
      }
    },
  },
  plugins: [],
  darkMode: 'class',
}

