#!/usr/bin/env python3
"""
Тестовое приложение для проверки переменных окружения
"""

import os
import sys
from datetime import datetime

def print_env_vars():
    """Выводит все переменные окружения"""
    print("=" * 60)
    print(f"Время: {datetime.now().isoformat()}")
    print("=" * 60)
    print("\n📋 ВСЕ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ:\n")
    
    # Сортируем и выводим все переменные
    for key in sorted(os.environ.keys()):
        value = os.environ[key]
        # Скрываем чувствительные данные
        if any(s in key.lower() for s in ['password', 'secret', 'token', 'key']):
            value = '***REDACTED***'
        print(f"  {key}={value}")
    
    print("\n" + "=" * 60)
    print("\n🔍 КЛЮЧЕВЫЕ ПЕРЕМЕННЫЕ:\n")
    
    # Ключевые переменные для проверки
    important_vars = [
        'MINIO_HOST',
        'MINIO_PORT', 
        'MINIO_ROOT_USER',
        'MINIO_ROOT_PASSWORD',
        'POSTGRES_HOST',
        'POSTGRES_PORT',
        'POSTGRES_USER',
        'POSTGRES_PASSWORD',
        'POSTGRES_DB',
        'KAFKA_BOOTSTRAP_SERVERS',
        'JWT_SECRET',
        'DATABASE_URL',
    ]
    
    for var in important_vars:
        value = os.environ.get(var, '❌ НЕ ЗАДАНА')
        if any(s in var.lower() for s in ['password', 'secret', 'token', 'key']):
            if value != '❌ НЕ ЗАДАНА':
                value = '***REDACTED***'
        print(f"  {var}: {value}")
    
    print("\n" + "=" * 60)
    
    # Проверка на пустые значения
    print("\n⚠️  ПУСТЫЕ ПЕРЕМЕННЫЕ:\n")
    empty_vars = []
    for var in important_vars:
        value = os.environ.get(var, '')
        if value == '' or value == '❌ НЕ ЗАДАНА':
            empty_vars.append(var)
    
    if empty_vars:
        for var in empty_vars:
            print(f"  ❌ {var} - ПУСТАЯ!")
    else:
        print("  ✅ Все ключевые переменные заданы!")
    
    print("\n" + "=" * 60)
    
    return len(empty_vars) == 0

if __name__ == "__main__":
    success = print_env_vars()
    
    # Выходим с кодом ошибки если есть пустые переменные
    sys.exit(0 if success else 1)
