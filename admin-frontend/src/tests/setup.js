import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Мокаем браузерные API
global.URL.createObjectURL = vi.fn(() => 'blob:test')
global.URL.revokeObjectURL = vi.fn()

// Мокаем fetch
global.fetch = vi.fn()

// global.FormData = vi.fn(() => ({
//   append: vi.fn()
// }))
// global.File = vi.fn()

// Очищаем моки после каждого теста
afterEach(() => {
  vi.clearAllMocks()
})
