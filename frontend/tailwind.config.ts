import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        gridiron: {
          950: "#090d16",
          900: "#0f172a",
          800: "#1e293b",
          700: "#334155",
          600: "#475569",
          500: "#64748b",
          accent: "#10b981",
          gold: "#f59e0b",
          crimson: "#ef4444",
          cyan: "#06b6d4",
          purple: "#8b5cf6",
        }
      }
    },
  },
  plugins: [],
};
export default config;
