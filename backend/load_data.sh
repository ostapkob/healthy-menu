#!/bin/bash

set -o allexport
source .env
set +o allexport

DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}"

function execute_copy {
    psql "$DATABASE_URL" -c "\copy $1 FROM '$2' WITH CSV HEADER;"
}

execute_copy "vitamins(id, name, short_name)" "./csv_data/vitamins.csv"
execute_copy "organs(id, name, description)" "./csv_data/organs.csv"
execute_copy "vitamin_organ_benefits(id, vitamin_id, organ_id, benefit_note)" "./csv_data/vitamin_organ_benefits.csv"
execute_copy "daily_vitamin_requirements(id, vitamin_id, amount, age_group)" "./csv_data/daily_vitamin_requirements.csv"
execute_copy "dishes(id, name, price)" "./csv_data/dishes.csv"
execute_copy "ingredients(id, name)" "./csv_data/ingredients.csv"
execute_copy "dish_ingredients(id, dish_id, ingredient_id, amount_grams)" "./csv_data/dish_ingredients.csv"
execute_copy "ingredient_vitamin_contents(id, ingredient_id, vitamin_id, content_per_100g)" "./csv_data/ingredient_vitamin_contents.csv"
execute_copy "courier(id, name, status, current_order_id)" "./csv_data/courier.csv


