/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "rgb(var(--color-primary) / <alpha-value>)",
        "primary-dark": "rgb(var(--color-primary-dark) / <alpha-value>)",
        "primary-light": "rgb(var(--color-primary-light) / <alpha-value>)",

        secondary: "rgb(var(--color-secondary) / <alpha-value>)",
        "secondary-dark": "rgb(var(--color-secondary-dark) / <alpha-value>)",
        "secondary-light": "rgb(var(--color-secondary-light) / <alpha-value>)",

        accent: "rgb(var(--color-accent) / <alpha-value>)",

        success: "rgb(var(--color-success) / <alpha-value>)",
        warning: "rgb(var(--color-warning) / <alpha-value>)",
        error: "rgb(var(--color-error) / <alpha-value>)",
        info: "rgb(var(--color-info) / <alpha-value>)",

        background: "rgb(var(--color-background) / <alpha-value>)",
        surface: "rgb(var(--color-surface) / <alpha-value>)",

        text: "rgb(var(--color-text-primary) / <alpha-value>)",
        "text-secondary": "rgb(var(--color-text-secondary) / <alpha-value>)",

        border: "rgb(var(--color-border) / <alpha-value>)",
      },
      fontFamily: {
        sans: ["var(--font-base)"],
      },
    },
  },
  plugins: [],
};
