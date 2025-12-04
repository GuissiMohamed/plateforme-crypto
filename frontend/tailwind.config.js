/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: "#0D1117",
        dark2: "#161B22",
        dark3: "#21262D",
        primary: "#58A6FF",
        accent: "#F0B90B",
        text: "#F0F6FC",
        text2: "#8B949E",
      },

      boxShadow: {
        "glow-yellow": "0 0 15px rgba(240,185,11,0.5)",
        "soft": "0 4px 8px rgba(0,0,0,0.4)",
      },

      transitionTimingFunction: {
        "soft": "cubic-bezier(0.16, 1, 0.3, 1)",
      },

      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(5px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideLeft: {
          "0%": { opacity: "0", transform: "translateX(20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        pulseAccent: {
          "0%, 100%": { boxShadow: "0 0 0px rgba(240,185,11,0.6)" },
          "50%": { boxShadow: "0 0 20px rgba(240,185,11,1)" },
        }
      },

      animation: {
        fadeIn: "fadeIn 0.4s ease-out",
        slideLeft: "slideLeft 0.4s ease-out",
        pulseAccent: "pulseAccent 1.5s infinite",
      }
    },
  },
  plugins: [],
}
