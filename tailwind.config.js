/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js' 
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',         // Blue
        'primary-dark': '#2563EB',
        secondary: '#1F2937',       // Dark Grey (for text, backgrounds)
        'secondary-dark': '#111827', // Almost black (for headings)
        accent: '#10B981',          // Green (for highlights, success)
        'neutral-lightest': '#F9FAFB', // Light Grey (bg)
        'neutral-lighter': '#F3F4F6',
        'neutral-light': '#E5E7EB',  // Lighter Grey (borders/dividers)
        'neutral-medium': '#D1D5DB', // Grey (borders/dividers)
        'neutral-dark': '#6B7280',   // Darker Grey (secondary text)
        'neutral-darker': '#4B5563',
        'neutral-darkest': '#374151',// Default text
        success: '#10B981',
        warning: '#F59E0B',         // Amber
        error: '#EF4444',           // Red
      },
      fontFamily: {
        primary: ['Inter', 'sans-serif'],
        secondary: ['Poppins', 'sans-serif'],
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
      },
      // Adding common spacing and animation delays from the example HTML for consistency
      // These can be used directly as Tailwind classes e.g. `delay-100`, `animate-fadeInUp`
      animation: {
        fadeInUp: 'fadeInUp 0.8s ease-out forwards',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
