# Stage 1: Зависимости
FROM node:20.19.0-alpine as deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Сборка
FROM node:20-alpine as builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build


# Stage 3: Production
FROM nginx:alpine

# Копируем статику из stage builder
COPY --from=builder /app/build /usr/share/nginx/html

# Копируем кастомную конфигурацию nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
