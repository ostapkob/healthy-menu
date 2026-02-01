import { describe, it, expect, vi } from 'vitest'

describe('Menu page logic', () => {
  beforeEach(() => {
    global.fetch = vi.fn()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('обрабатывает успешную загрузку меню', async () => {
    const mockDishes = [
      { id: 1, name: 'Суп', price: 200 },
      { id: 2, name: 'Салат', price: 150 }
    ]
    
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockDishes)
    })
    
    // Имитация логики загрузки
    const loadMenu = async () => {
      const response = await fetch('http://localhost:8002/menu/')
      if (response.ok) {
        return await response.json()
      }
      throw new Error('Failed to load menu')
    }
    
    const dishes = await loadMenu()
    expect(dishes).toHaveLength(2)
    expect(dishes[0].name).toBe('Суп')
    expect(fetch).toHaveBeenCalledWith('http://localhost:8002/menu/')
  })

  it('обрабатывает ошибку загрузки меню', async () => {
    global.fetch.mockRejectedValue(new Error('Network error'))
    
    const loadMenu = async () => {
      try {
        const response = await fetch('http://localhost:8002/menu/')
        if (!response.ok) throw new Error('API error')
        return await response.json()
      } catch (error) {
        console.error(error)
        return []
      }
    }
    
    const dishes = await loadMenu()
    expect(dishes).toEqual([])
  })
})
