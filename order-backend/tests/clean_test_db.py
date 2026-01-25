import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def clean_test_database():
    """Очищает тестовую БД"""
    TEST_DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    TEST_DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    TEST_DB_NAME = os.getenv("POSTGRES_TESTS_DB", "food_db_tests")
    TEST_DB_USER = os.getenv("POSTGRES_TESTS_USER", "postgres")
    TEST_DB_PASSWORD = os.getenv("POSTGRES_TEST_PASSWORD", "postgres")
    
    DATABASE_URL = f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Получаем список всех таблиц
        tables = conn.execute(text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)).fetchall()
        
        # Отключаем триггеры
        conn.execute(text("SET session_replication_role = 'replica'"))
        
        # Очищаем каждую таблицу
        for table in tables:
            conn.execute(text(f'TRUNCATE TABLE "{table[0]}" CASCADE'))
        
        # Включаем триггеры обратно
        conn.execute(text("SET session_replication_role = 'origin'"))
        
        conn.commit()
    
    print(f"✅ База данных {TEST_DB_NAME} успешно очищена")

if __name__ == "__main__":
    clean_test_database()
