import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Look for env files in the ui directory
  envDir: '.',
  envPrefix: 'VITE_'
})
