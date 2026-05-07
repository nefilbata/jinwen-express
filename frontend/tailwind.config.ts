import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        bronze: {
          50: '#FFFBF5',
          100: '#F5ECD7',
          200: '#E8D5A3',
          300: '#D4A84B',
          400: '#C4973A',
          500: '#B8860B',
          600: '#A07509',
          700: '#7D5C08',
          800: '#5D4037',
          900: '#3E2723',
        },
        ink: {
          DEFAULT: '#3E2723',
          light: '#5D4037',
          muted: '#8D6E63',
        },
        paper: {
          DEFAULT: '#FFFBF5',
          warm: '#FDF8F0',
          dark: '#F5ECD7',
        },
      },
      fontFamily: {
        serif: ['"Noto Serif SC"', '"SimSun"', 'serif'],
        sans: ['"Noto Sans SC"', '"Microsoft YaHei"', 'sans-serif'],
      },
      maxWidth: {
        digest: '720px',
      },
    },
  },
  plugins: [],
};

export default config;
