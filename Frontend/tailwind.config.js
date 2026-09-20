/** @type {import('tailwindcss').Config} */

const token = (name) => `rgb(var(--color-${name}) / <alpha-value>)`;

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: token("primary"),
        "primary-dark": token("primary-dark"),
        "primary-light": token("primary-light"),

        secondary: token("secondary"),
        "secondary-dark": token("secondary-dark"),
        "secondary-light": token("secondary-light"),

        accent: token("accent"),

        success: token("success"),
        warning: token("warning"),
        error: token("error"),
        info: token("info"),

        background: token("background"),
        surface: token("surface"),

        text: token("text-primary"),
        "text-secondary": token("text-secondary"),

        border: token("border"),

        foreground: token("foreground"),
        muted: token("muted"),
        "muted-foreground": token("muted-foreground"),

        "on-primary": token("on-primary"),
        "on-secondary": token("on-secondary"),
        "on-accent": token("on-accent"),
        "on-success": token("on-success"),
        "on-warning": token("on-warning"),
        "on-error": token("on-error"),
        "on-info": token("on-info"),

        scrim: token("scrim"),
        sheen: token("sheen"),
        star: token("star"),
        "star-empty": token("star-empty"),
      },
      borderRadius: {
        DEFAULT: "var(--border-radius)",
        md: "var(--border-radius)",
        lg: "calc(var(--border-radius) * 1.5)",
        xl: "calc(var(--border-radius) * 2)",
      },
      fontFamily: {
        sans: ["var(--font-base)"],
      },
      transitionDuration: {
        DEFAULT: "var(--transition-speed)",
      },
      screens: {
        sm: "640px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
        "2xl": "1536px",
      },
    },
  },
  plugins: [],
};
