import { defineConfig } from 'vitest/config'
import { sveltekit } from '@sveltejs/kit/vite'

export default defineConfig({
  plugins: [sveltekit()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.js'],
    include: ['src/**/*.{test,spec}.{js,ts}'],
    globals: true,
    // Игнорируем предупреждения Svelte в тестах
    onConsoleLog: (log, type) => {
      if (type === 'warning' && log.includes('A11y') || log.includes('Self-closing')) {
        return false // игнорируем
      }
    }
  }
})
