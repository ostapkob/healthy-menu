import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Мокаем SvelteKit stores
vi.mock('$app/stores', () => {
  return {
    page: {
      subscribe: vi.fn((fn) => {
        fn({ url: new URL('http://localhost'), params: {} })
        return () => {}
      })
    },
    navigating: { subscribe: vi.fn(() => () => {}) }
  }
})

// Мокаем fetch
global.fetch = vi.fn()

// Мокаем window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  })),
})

// Очищаем моки после каждого теста
afterEach(() => {
  vi.clearAllMocks()
})
