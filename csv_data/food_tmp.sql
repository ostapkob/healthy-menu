-- Создать функцию очистки названий продуктов
CREATE OR REPLACE FUNCTION clean_food_name(description TEXT) 
RETURNS TEXT AS $$
DECLARE
    cleaned_text TEXT;
BEGIN
    -- Начинаем обработку
    cleaned_text := description;
    -- Удаляем всё после region/pass/store и т.д.
    cleaned_text := REGEXP_REPLACE(cleaned_text, '\s*(region|pass|store|brand|from|with\s+added).*', '', 'gi');
    -- Удаляем паттерны с цифрами, NFY и скобки
    cleaned_text := REGEXP_REPLACE(cleaned_text, '\(.*|\S*\d+\S*', '', 'g');
    -- Удаляем ключевые слова
    cleaned_text := REGEXP_REPLACE(cleaned_text,
        '\m(vitamin\s+[abcdek]|minerals|fa|fish|cheese|carotenoids|nuts|oil|cholesterol|proximates|restaurant|vitamin|vit\s+[abcdek]|amino\s+acids|total\s+fat|tocopherols|mushroom|mushrooms|thiamin|tdf|sugars|starch|selenium|and|fatty\s+acids|riboflavin|retinol|fat|folate|niacin|pantothenic\s+acid)\M',
        '', 'gi');
    -- Приводим к нижнему регистру
    cleaned_text := LOWER(cleaned_text);
    -- Удаляем запятые: заменяем запятые с пробелами на пробел
    cleaned_text := REGEXP_REPLACE(cleaned_text, '\s*,\s*', ' ', 'g');
    -- Удаляем дефисы: заменяем дефисы с пробелами на пробел
    cleaned_text := REGEXP_REPLACE(cleaned_text, '\s*-\s*', ' ', 'g');
    -- Удаляем лишние пробелы (двойные, тройные и т.д.)
    cleaned_text := REGEXP_REPLACE(cleaned_text, '\s+', ' ', 'g');
    -- Удаляем пробелы и запятые/дефисы в начале и конце
    cleaned_text := TRIM(cleaned_text);
    cleaned_text := TRIM(BOTH ', -' FROM cleaned_text);
    RETURN cleaned_text;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

drop table if exists food_tmp;

create table food_tmp as 
select id as fdc_id
     , name as description
     , food_category_id 
  from (select id
	     , name 
	     , food_category_id 
	     , count(1) as cnt
	     , row_number() over (partition by name order by count(1) desc) as rn
	     , array_length(regexp_split_to_array(name, '\s+'), 1)  as word_count
	  from (
		SELECT f.fdc_id as id 
		     , clean_food_name(f.description) as name
		     , n.name as nutrient
		     , food_category_id 
		  from food f
		  join food_nutrient fn 
		    on f.fdc_id = fn.fdc_id
		  join nutrient n 
		    on n.id = fn.nutrient_id
	       )
	 group by id, name, food_category_id 
)
where rn = 1
  and cnt > 15
  and name <> ''
  and name  !~ 'american|breakfast|added|cooked'
  and word_count < 4
;


-- ========================================
-- ✅ БЕЗОПАСНОЕ ОБНОВЛЕНИЕ food из food_tmp
-- ========================================

-- 1. ✅ СОЗДАТЬ backup ТОЛЬКО fdc_id (для проверки)
CREATE TEMP TABLE food_backup AS 
SELECT fdc_id FROM food;

-- 2. ✅ УДАЛИТЬ ВСЕ внешние ключи (безопасно)
ALTER TABLE food_nutrient DROP CONSTRAINT IF EXISTS food_nutrient_fdc_id_fkey;
ALTER TABLE food_ru DROP CONSTRAINT IF EXISTS food_ru_fdc_id_fkey;
ALTER TABLE food DROP CONSTRAINT IF EXISTS food_food_category_id_fkey;

-- 3. ✅ УДАЛИТЬ таблицу food (CASCADE удалит связанные данные)
DROP TABLE IF EXISTS food CASCADE;

-- 4. ✅ Переименовать food_tmp → food
ALTER TABLE food_tmp RENAME TO food;

-- 5. ✅ ДОБАВИТЬ PRIMARY KEY ПЕРВЫМ (обязательно!)
ALTER TABLE food ADD PRIMARY KEY (fdc_id);

-- 6. ✅ Восстановить FK food → food_category
ALTER TABLE food ADD CONSTRAINT food_food_category_id_fkey 
    FOREIGN KEY (food_category_id) REFERENCES food_category(id);

-- 7. ✅ ОЧИСТИТЬ связанные таблицы от осиротевших записей
DELETE FROM food_nutrient WHERE fdc_id NOT IN (SELECT fdc_id FROM food);
DELETE FROM food_ru WHERE fdc_id NOT IN (SELECT fdc_id FROM food);

-- 8. ✅ Восстановить FK food_nutrient → food
ALTER TABLE food_nutrient ADD CONSTRAINT food_nutrient_fdc_id_fkey 
    FOREIGN KEY (fdc_id) REFERENCES food(fdc_id) ON DELETE CASCADE;

-- 9. ✅ Восстановить FK food_ru → food
ALTER TABLE food_ru ADD CONSTRAINT food_ru_fdc_id_fkey 
    FOREIGN KEY (fdc_id) REFERENCES food(fdc_id) ON DELETE CASCADE;

-- 10. ✅ Удалить backup
DROP TABLE food_backup;

-- 11. ✅ ПРОВЕРКА целостности
DO $$
DECLARE
    food_count INTEGER := (SELECT COUNT(*) FROM food);
    nutr_count INTEGER := (SELECT COUNT(*) FROM food_nutrient);
    ru_count INTEGER := (SELECT COUNT(*) FROM food_ru);
    orphans_nutr INTEGER;
    orphans_ru INTEGER;
BEGIN
    -- Проверка на осиротевшие записи
    SELECT COUNT(*) INTO orphans_nutr FROM food_nutrient fn 
        LEFT JOIN food f ON fn.fdc_id = f.fdc_id WHERE f.fdc_id IS NULL;
    SELECT COUNT(*) INTO orphans_ru FROM food_ru fr 
        LEFT JOIN food f ON fr.fdc_id = f.fdc_id WHERE f.fdc_id IS NULL;
    
    RAISE NOTICE '✅ Обновление завершено!';
    RAISE NOTICE '📊 Статистика: food=%, food_nutrient=%, food_ru=%', 
        food_count, nutr_count, ru_count;
    RAISE NOTICE '🔍 Осиротевших: nutrient=%, ru=%', orphans_nutr, orphans_ru;
    
    IF orphans_nutr > 0 OR orphans_ru > 0 THEN
        RAISE EXCEPTION '❌ Остались осиротевшие записи!';
    END IF;
END $$;

