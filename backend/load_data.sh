#!/bin/bash

set -o allexport
source .env
set +o allexport

DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}"

function execute_copy {
    psql "$DATABASE_URL" -c "\copy $1 FROM '$2' WITH CSV HEADER;"
}

# Справочник нутриентов (витамины + минералы)
execute_copy "nutrients(id,name,short_name,type,unit,code)" "./csv_data/vitamins_minerals_extended.csv"

# Органы и их описание
execute_copy "organs(id, name, description)" "./csv_data/organs.csv"

# Польза нутриента для органа
execute_copy "nutrient_organ_benefits(id, nutrient_id, organ_id, benefit_note)" "./csv_data/vitamin_organ_benefits.csv"

# Суточные нормы нутриентов
execute_copy "daily_nutrient_requirements(id, nutrient_id, amount, age_group)" "./csv_data/daily_requirements_extended.csv"

# Блюда (обновлённый список популярных блюд)
execute_copy "dishes(id, name, price, description)" "./csv_data/popular_dishes.csv"

# Ингредиенты (расширенный список)
execute_copy "ingredients(id, name, category)" "./csv_data/ingredients_extended.csv"

# Состав блюд (рецепты)
execute_copy "dish_ingredients(id, dish_id, ingredient_id, amount_grams)" "./csv_data/dish_composition.csv"

# Содержание нутриентов в ингредиентах
execute_copy "ingredient_nutrient_contents(id, ingredient_id, nutrient_id, content_per_100g)" "./csv_data/ingredient_nutrient_content.csv"

# Калории и БЖУ ингредиентов (если есть отдельная таблица, например ingredients_calories)
execute_copy "ingredient_calories(id, ingredient_id, calories_per_100g, protein_g, fat_g, carbs_g)" "./csv_data/ingredient_calories.csv"

# Курьеры (исправлена кавычка в конце)
execute_copy "couriers(id, name, status, current_order_id)" "./csv_data/courier.csv"

