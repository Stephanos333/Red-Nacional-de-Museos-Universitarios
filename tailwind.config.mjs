/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        brand: {
          burgundy: {
            50: '#fdf3f4',
            100: '#fbe6e8',
            200: '#f7d0d4',
            300: '#f0abb3',
            400: '#e57c89',
            500: '#d54f60',
            600: '#bf3346',
            700: '#a02536',
            800: '#852230',
            900: '#71212d',
            950: '#3f0c13',
          },
          navy: {
            50: '#f0f5fa',
            100: '#deebf5',
            200: '#c3dbed',
            300: '#99c3e0',
            400: '#67a3cf',
            500: '#4386bd',
            600: '#326ca1',
            700: '#295682',
            800: '#254a6d',
            900: '#1e3a5f',
            950: '#13253e',
          },
          gold: {
            50: '#fbf9ed',
            100: '#f5f0d2',
            200: '#ede1a7',
            300: '#e1cb73',
            400: '#d5b345',
            500: '#c59b27',
            600: '#a97a1d',
            700: '#845719',
            800: '#6f471a',
            900: '#5e3c1b',
            950: '#36200c',
          },
          parchment: {
            50: '#faf9f6',
            100: '#f4f2ec',
            200: '#eae6db',
            300: '#ded7c5',
            400: '#c9bfa7',
            500: '#b4a58b',
          }
        }
      },
      fontFamily: {
        // Pilas de fuentes nativas del sistema: cero descargas y cero envío de IPs a terceros.
        sans: ['ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', '"Noto Sans"', 'sans-serif'],
        serif: ['ui-serif', 'Georgia', 'Cambria', '"Times New Roman"', 'Times', 'serif'],
      }
    },
  },
  plugins: [],
};
