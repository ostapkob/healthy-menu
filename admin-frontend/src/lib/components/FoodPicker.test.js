import { describe, it, expect, vi } from 'vitest'

describe('ImageUpload logic', () => {
  it('должен проверять типы файлов', () => {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    
    const isValidType = (type) => allowedTypes.includes(type)
    
    expect(isValidType('image/jpeg')).toBe(true)
    expect(isValidType('image/png')).toBe(true)
    expect(isValidType('image/gif')).toBe(false)
    expect(isValidType('application/pdf')).toBe(false)
  })
})
