import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'node:fs'
import path from 'node:path'

const componentOutput = path.resolve('dist-streamlit')

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'rename-streamlit-component-entry',
      closeBundle() {
        const source = path.join(componentOutput, 'streamlit-index.html')
        const target = path.join(componentOutput, 'index.html')
        if (fs.existsSync(source)) fs.renameSync(source, target)
      },
    },
  ],
  root: '.',
  base: './',
  build: {
    outDir: 'dist-streamlit',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        index: 'streamlit-index.html',
      },
    },
  },
})