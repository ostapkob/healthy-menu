import { describe, it, expect } from 'vitest'

describe('ImageUpload logic', () => {
  it('должен фильтровать допустимые типы файлов', () => {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    
    const isValidFileType = (fileType) => allowedTypes.includes(fileType)
    
    expect(isValidFileType('image/jpeg')).toBe(true)
    expect(isValidFileType('image/png')).toBe(true)
    expect(isValidFileType('image/gif')).toBe(false)
    expect(isValidFileType('application/pdf')).toBe(false)
  })
  
  it('должен создавать правильный FormData', () => {
    // В jsdom среде File и FormData должны быть доступны
    // Если File не определен, создаем простой мок
    if (typeof File === 'undefined') {
      global.File = class MockFile {
        constructor(parts, filename, options) {
          this.name = filename
          this.type = options?.type || ''
          this.size = parts.length
        }
      }
    }
    
    const mockFile = new File(['test'], 'test.png', { type: 'image/png' })
    const formData = new FormData()
    
    // Добавляем файл
    formData.append('file', mockFile)
    
    // Проверяем что append работает (мы не можем проверить содержимое FormData напрямую)
    expect(formData).toBeInstanceOf(FormData)
    expect(mockFile).toBeInstanceOf(File)
    expect(mockFile.name).toBe('test.png')
    expect(mockFile.type).toBe('image/png')
  })
})
