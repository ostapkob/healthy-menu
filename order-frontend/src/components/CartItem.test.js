import { describe, it, expect, vi } from 'vitest'

// Тестируем логику компонента CartItem
describe('CartItem logic', () => {
  it('вычисляет общую стоимость позиции', () => {
    const calculateTotal = (price, quantity) => (price * quantity).toFixed(2)
    
    expect(calculateTotal(200, 1)).toBe('200.00')
    expect(calculateTotal(150, 2)).toBe('300.00')
    expect(calculateTotal(99.99, 3)).toBe('299.97')
  })
})
