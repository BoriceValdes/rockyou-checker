/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Palette volontairement limitée à 3 couleurs principales
        // (+ nuances neutres) pour un rendu sobre et cohérent.
        ink: {
          DEFAULT: "#0F1225",   // fond très sombre
          light: "#1B2040",
        },
        signal: {
          DEFAULT: "#6C5CE7",   // couleur d'accent (violet)
          soft: "#A29BFE",
        },
        alert: {
          DEFAULT: "#FF6B6B",   // couleur d'alerte (rouge corail)
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
