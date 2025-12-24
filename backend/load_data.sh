#!/bin/bash
# csvcut -c fdc_id,description,food_category_id FoodData_Central_foundation_food_csv_2025-12-18/food.csv > food.csv

set -o allexport
source .env
set +o allexport

echo ${DATABASE_URL}

function execute_copy {

    psql "${DATABASE_URL}" -c "\copy $1 FROM '$2' WITH CSV HEADER;"
}


# Nutrients
csvcut -c id,name,unit_name,nutrient_nbr ./csv_data/FoodData_Central_foundation_food_csv_2025-12-18/nutrient.csv > ./csv_data/nutrient.csv
execute_copy "nutrient(id,name,unit_name,nutrient_nbr)" "./csv_data/nutrient.csv" 

# # Food
csvcut -c fdc_id,description,food_category_id ./csv_data/FoodData_Central_foundation_food_csv_2025-12-18/food.csv > ./csv_data/food.csv
execute_copy "food(fdc_id,description,food_category_id)" "./csv_data/food.csv"

#связь
csvcut -c id,fdc_id,nutrient_id,amount ./csv_data/FoodData_Central_foundation_food_csv_2025-12-18/food_nutrient.csv > ./csv_data/food_nutrient.csv
execute_copy "food_nutrient(id,fdc_id,nutrient_id,amount)" "./csv_data/food_nutrient.csv"

# Русская локализация
# execute_copy "food_ru(fdc_id,name_ru,description_ru)" "./csv_data/food_ru.csv"
# execute_copy "nutrient_ru(nutrient_id,name_ru,unit_ru)" "./csv_data/nutrient_ru.csv"

# Органы и их описание
# execute_copy "organs(id, name, description)" "./csv_data/organs.csv"

# Польза нутриента для органа
# execute_copy "nutrient_organ_benefits(id, nutrient_id, organ_id, benefit_note)" "./csv_data/vitamin_organ_benefits.csv"

# Суточные нормы нутриентов
# execute_copy "daily_nutrient_requirements(id, nutrient_id, amount, age_group)" "./csv_data/daily_requirements_extended.csv"

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
# execute_copy "couriers(id, name, status, current_order_id)" "./csv_data/courier.csv"

# INDEXES
# psql "$DATABASE_URL" -c "CREATE INDEX IF NOT EXISTS idx_food_fdc_id ON food(fdc_id);"
# psql "$DATABASE_URL" -c "CREATE INDEX IF NOT EXISTS idx_food_nutrient_fdc ON food_nutrient(fdc_id);"
# psql "$DATABASE_URL" -c "CREATE INDEX IF NOT EXISTS idx_food_nutrient_nutr ON food_nutrient(nutrient_id);"
# psql "$DATABASE_URL" -c "CREATE INDEX IF NOT EXISTS idx_food_ru_fdc ON food_ru(fdc_id);"
# psql "$DATABASE_URL" -c "CREATE INDEX IF NOT EXISTS idx_nutr_ru_id ON nutrient_ru(nutrient_id);"
