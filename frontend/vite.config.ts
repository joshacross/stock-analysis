import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // When running npm run dev on host: backend is at localhost:8888.
      // In Docker, the frontend is served by nginx (no Vite proxy); use service name only if Vite runs inside Docker.
      "/api": {
        target: "http://127.0.0.1:8888",
        changeOrigin: true,
      },
    },
  },
});
