FROM food-main:latest

COPY . /app/courier

WORKDIR /app/courier

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
