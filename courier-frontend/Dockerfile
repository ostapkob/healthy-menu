# Stage 1: Зависимости
FROM node:20.19.0-alpine as deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Сборка
FROM node:20-alpine as builder

# Объявляем ARG в Stage 2
ARG API_BASE_URL='http://localhost:8003'
ARG SVELTEKIT_BASEPATH=""
ARG WEB_SOCKET_URL='ws://localhost:8003'
ENV VITE_API_BASE_URL=$API_BASE_URL
ENV SVELTEKIT_BASEPATH=$SVELTEKIT_BASEPATH
ENV VITE_WEB_SOCKET_URL=$WEB_SOCKET_URL

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Production
FROM nginx:alpine

# Повторяем ARG в Stage 3
ARG API_BASE_URL='http://localhost:8003'
ARG WEB_SOCKET_URL='ws://localhost:8003'
ENV VITE_API_BASE_URL=$API_BASE_URL
ENV VITE_WEB_SOCKET_URL=$WEB_SOCKET_URL

# Копируем статику из stage builder
COPY --from=builder /app/build /usr/share/nginx/html

# Копируем кастомную конфигурацию nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
