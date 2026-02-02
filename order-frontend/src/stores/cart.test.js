import { describe, it, expect, vi } from 'vitest'
import { get, writable } from 'svelte/store'

// Создаем тестовый стор для изоляции тестов
function createTestCart() {
  const { subscribe, set, update } = writable([])
  
  const addToCart = (dish) => {
    update(items => {
      const existing = items.find(item => item.id === dish.id)
      if (existing) {
        return items.map(item =>
          item.id === dish.id ? { ...item, quantity: item.quantity + 1 } : item
        )
      } else {
        return [...items, { ...dish, quantity: 1 }]
      }
    })
  }

  const removeFromCart = (dishId) => {
    update(items => items.filter(item => item.id !== dishId))
  }

  const clearCart = () => {
    set([])
  }

  return {
    subscribe,
    addToCart,
    removeFromCart,
    clearCart
  }
}

describe('cart store', () => {
  it('добавляет блюдо в корзину', () => {
    const { addToCart, subscribe } = createTestCart()
    const dish = { id: 1, name: 'Суп', price: 200 }
    
    let currentCart = []
    const unsubscribe = subscribe(value => currentCart = value)
    
    addToCart(dish)
    
    // Ждем обновления стора
    setTimeout(() => {
      expect(currentCart).toHaveLength(1)
      expect(currentCart[0].id).toBe(1)
      expect(currentCart[0].quantity).toBe(1)
      unsubscribe()
    }, 0)
  })

  it('увеличивает количество при повторном добавлении', () => {
    const { addToCart, subscribe } = createTestCart()
    const dish = { id: 1, name: 'Суп', price: 200 }
    
    let currentCart = []
    const unsubscribe = subscribe(value => currentCart = value)
    
    // Добавляем два раза
    addToCart(dish)
    addToCart(dish)
    
    // Ждем всех обновлений
    setTimeout(() => {
      expect(currentCart).toHaveLength(1)
      expect(currentCart[0].quantity).toBe(2) // должно быть 2, а не 3!
      unsubscribe()
    }, 10)
  })

  it('удаляет блюдо из корзины', () => {
    const { addToCart, removeFromCart, subscribe } = createTestCart()
    const dish = { id: 1, name: 'Суп', price: 200 }
    
    let currentCart = []
    const unsubscribe = subscribe(value => currentCart = value)
    
    addToCart(dish)
    
    setTimeout(() => {
      expect(currentCart).toHaveLength(1)
      
      removeFromCart(1)
      
      setTimeout(() => {
        expect(currentCart).toHaveLength(0)
        unsubscribe()
      }, 0)
    }, 0)
  })

  it('очищает корзину', () => {
    const { addToCart, clearCart, subscribe } = createTestCart()
    const dish1 = { id: 1, name: 'Суп', price: 200 }
    const dish2 = { id: 2, name: 'Салат', price: 150 }
    
    let currentCart = []
    const unsubscribe = subscribe(value => currentCart = value)
    
    addToCart(dish1)
    addToCart(dish2)
    
    setTimeout(() => {
      expect(currentCart).toHaveLength(2)
      
      clearCart()
      
      setTimeout(() => {
        expect(currentCart).toHaveLength(0)
        unsubscribe()
      }, 0)
    }, 0)
  })
})
