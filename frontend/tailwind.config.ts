import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#030712",
        glass: "rgba(15, 23, 42, 0.62)",
        neon: "#7c3aed",
        cyanGlow: "#06b6d4",
      },
      boxShadow: {
        glow: "0 24px 80px rgba(124, 58, 237, 0.28)",
      },
    },
  },
  plugins: [],
};

export default config;
