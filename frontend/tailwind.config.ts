import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#101828",
        mist: "#f4f7fb",
        steel: "#475467",
        signal: "#0f766e",
        ember: "#c2410c",
        sun: "#f59e0b"
      },
      boxShadow: {
        panel: "0 24px 60px rgba(16, 24, 40, 0.10)"
      },
      borderRadius: {
        "4xl": "2rem"
      }
    }
  },
  plugins: []
};

export default config;
