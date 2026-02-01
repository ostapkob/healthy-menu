import { describe, it, expect, vi } from 'vitest'

describe('Dishes page logic', () => {
  it('должен фильтровать блюда после удаления', () => {
    const dishes = [
      { id: 1, name: 'Суп', price: 200 },
      { id: 2, name: 'Салат', price: 150 },
      { id: 3, name: 'Десерт', price: 100 }
    ]
    
    const deleteDish = (id, dishesArray) => {
      return dishesArray.filter(d => d.id !== id)
    }
    
    const result = deleteDish(2, dishes)
    expect(result).toHaveLength(2)
    expect(result.find(d => d.id === 2)).toBeUndefined()
    expect(result.find(d => d.id === 1)).toBeDefined()
  })
})
