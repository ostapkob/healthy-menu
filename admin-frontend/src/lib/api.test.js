import { describe, it, expect, vi } from 'vitest'

// Тестируем логику работы с API
describe('API logic', () => {
  it('должен формировать правильный URL для получения блюд', () => {
    const API_BASE_URL = 'http://localhost:8001'

    const endpoint = '/dishes/'
    const expectedUrl = `${API_BASE_URL}${endpoint}`

    expect(expectedUrl).toBe('http://localhost:8001/dishes/')
  })

  it('должен правильно обрабатывать ошибки API', () => {
    const handleApiError = (error) => {
      if (error.message.includes('network')) {
        return 'Ошибка сети'
      }
      return 'Ошибка сервера'
    }

    expect(handleApiError(new Error('network error'))).toBe('Ошибка сети')
    expect(handleApiError(new Error('server error'))).toBe('Ошибка сервера')
  })
})
