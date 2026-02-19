#!/bin/bash
# csvcut -c fdc_id,description,food_category_id FoodData_Central_foundation_food_csv_2025-12-18/food.csv > food.csv

set -o allexport
source .env
set +o allexport


function execute_copy {

    psql "${POSTGRES_DATABASE_URL}" -c "\copy $1 FROM '$2' WITH CSV HEADER;"
}

# Удаление лишних коллонок из оригинального источника
csvcut -c id,name,unit_name,nutrient_nbr ./csv_data/FoodData_Central_foundation_food_csv_2025-12-18/nutrient.csv > ./csv_data/nutrient.csv
csvcut -c fdc_id,description,food_category_id ./csv_data/FoodData_Central_foundation_food_csv_2025-12-18/food.csv > ./csv_data/food.csv
csvcut -c id,fdc_id,nutrient_id,amount ./csv_data/FoodData_Central_foundation_food_csv_2025-12-18/food_nutrient.csv > ./csv_data/food_nutrient.csv


# Nutrients
execute_copy "nutrient(id,name,unit_name,nutrient_nbr)" "./csv_data/nutrient.csv" 
 
# # Food Category
execute_copy "food_category(id,code,description)" "./csv_data/food_category.csv"

# # Food
execute_copy "food(fdc_id,description,food_category_id)" "./csv_data/food.csv"

#связь
execute_copy "food_nutrient(id,fdc_id,nutrient_id,amount)" "./csv_data/food_nutrient.csv"

 
# Суточные нормы нутриентов
execute_copy "daily_norms(nutrient_id,amount,unit_name,source)" "./csv_data/daily_norms.csv"


# Русская локализация
execute_copy "food_ru(id,fdc_id,name_ru,food_category_id)" "./csv_data/food_ru.csv"
execute_copy "nutrient_ru(id,nutrient_id,name_ru)" "./csv_data/nutrient_ru.csv"
execute_copy "food_category_ru(category_id,name_ru,description_ru)" "./csv_data/food_category_ru.csv"

psql "${POSTGRES_DATABASE_URL}" -f ./csv_data/food_tmp.sql

# export
# psql "${POSTGRES_DATABASE_URL}" -c "\copy food_tmp TO './csv_data/food_tmp.csv' DELIMITER ',' CSV HEADER"


# Органы и их описание
# execute_copy "organs(id, name, description)" "./csv_data/organs.csv"

# Польза нутриента для органа
# execute_copy "nutrient_organ_benefits(id, nutrient_id, organ_id, benefit_note)" "./csv_data/vitamin_organ_benefits.csv"


# Блюда (обновлённый список популярных блюд)
# execute_copy "dishes(id, name, price, description)" "./csv_data/popular_dishes.csv"

# Ингредиенты (расширенный список)
# execute_copy "ingredients(id, name, category)" "./csv_data/ingredients_extended.csv"

# Состав блюд (рецепты)
# execute_copy "dish_ingredients(id, dish_id, ingredient_id, amount_grams)" "./csv_data/dish_composition.csv"

# Содержание нутриентов в ингредиентах
# execute_copy "ingredient_nutrient_contents(id, ingredient_id, nutrient_id, content_per_100g)" "./csv_data/ingredient_nutrient_content.csv"

# Калории и БЖУ ингредиентов (если есть отдельная таблица, например ingredients_calories)
# execute_copy "ingredient_calories(id, ingredient_id, calories_per_100g, protein_g, fat_g, carbs_g)" "./csv_data/ingredient_calories.csv"

# Курьеры
execute_copy "couriers(id, name, status, current_order_id)" "./csv_data/courier.csv"

# INDEXES
psql "$POSTGRES_DATABASE_URL" -c "CREATE INDEX IF NOT EXISTS idx_food_fdc_id ON food(fdc_id);"
psql "$POSTGRES_DATABASE_URL" -c "CREATE INDEX IF NOT EXISTS idx_food_nutrient_fdc ON food_nutrient(fdc_id);"
psql "$POSTGRES_DATABASE_URL" -c "CREATE INDEX IF NOT EXISTS idx_food_nutrient_nutr ON food_nutrient(nutrient_id);"
psql "$POSTGRES_DATABASE_URL" -c "CREATE INDEX IF NOT EXISTS idx_food_ru_fdc ON food_ru(fdc_id);"
psql "$POSTGRES_DATABASE_URL" -c "CREATE INDEX IF NOT EXISTS idx_nutr_ru_id ON nutrient_ru(nutrient_id);"

# Test DataBase
psql "$POSTGRES_DATABASE_URL" -c "CREATE DATABASE food_db_tests WITH TEMPLATE food_db;"
