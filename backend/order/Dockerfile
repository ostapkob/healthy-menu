FROM food-main:latest

COPY . /app/order

WORKDIR /app/order

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
