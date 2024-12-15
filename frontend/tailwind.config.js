/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
  theme: {
    extend: {
      colors: {
        zinc: {
          800: "#27272a",
          900: "#18181b",
        },
      },
    },
  },
  plugins: [],
};
