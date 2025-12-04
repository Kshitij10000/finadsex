import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  allowedHosts: [
      '771747c2af6a.ngrok-free.app',
      'localhost',
      '127.0.0.1',
      '::1'
    ]
})
