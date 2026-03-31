# Prometheus метрики в backend'ах

## 📊 Принцип работы

Prometheus работает по принципу **pull** (вытягивание):

```
┌─────────────┐      GET /metrics      ┌──────────────┐
│  Prometheus │ ──────────────────────► │   Backend    │
│  (каждые 30с)│ ◄────────────────────── │  (FastAPI)   │
│             │      текст в формате    │              │
│             │      Prometheus         │              │
└─────────────┘                         └──────────────┘
```

## 🔧 Что добавлено

### 1. Библиотека `prometheus-client`

Установлена в requirements.txt всех backend'ов:
```
prometheus-client==0.21.1
```

### 2. Endpoint `/metrics`

Каждый backend теперь имеет endpoint `/metrics` который отдает метрики в формате Prometheus.

Пример ответа:
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/v1/admin/foods/",status="200"} 42.0
http_requests_total{method="POST",endpoint="/api/v1/admin/dishes/",status="201"} 15.0

# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",endpoint="/api/v1/admin/foods/",le="0.005"} 35.0
http_request_duration_seconds_bucket{method="GET",endpoint="/api/v1/admin/foods/",le="0.01"} 40.0
http_request_duration_seconds_sum{method="GET",endpoint="/api/v1/admin/foods/"} 0.523
http_request_duration_seconds_count{method="GET",endpoint="/api/v1/admin/foods/"} 42.0
```

### 3. Middleware для сбора метрик

Каждый запрос автоматически логируется:
- **REQUEST_COUNT** - количество запросов (method, endpoint, status)
- **REQUEST_DURATION** - время выполнения запроса (method, endpoint)

## 📈 Типы метрик

### Counter (Счетчик)
Метрика которая только растет:
```promql
# Количество запросов
http_requests_total{app="admin-backend", method="GET"}

# Скорость запросов в секунду
rate(http_requests_total{app="admin-backend"}[5m])
```

### Histogram (Гистограмма)
Метрика для измерения времени/размеров:
```promql
# Среднее время запроса
rate(http_request_duration_seconds_sum{app="admin-backend"}[5m]) / 
rate(http_request_duration_seconds_count{app="admin-backend"}[5m])

# 95-й перцентиль
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket{app="admin-backend"}[5m])
)
```

## 🔍 Примеры запросов Prometheus

```promql
# Статус backend'ов (1 = up, 0 = down)
up{app=~".*-backend"}

# Запросов в секунду по backend'ам
sum by (app) (rate(http_requests_total{app=~".*-backend"}[5m]))

# Ошибки (5xx статусы)
sum by (app) (rate(http_requests_total{app=~".*-backend",status=~"5.."}[5m]))

# Среднее время ответа
sum by (app) (
  rate(http_request_duration_seconds_sum{app=~".*-backend"}[5m]) 
  / 
  rate(http_request_duration_seconds_count{app=~".*-backend"}[5m])
)

# 95-й перцентиль времени ответа
histogram_quantile(0.95, 
  sum by (app, le) (
    rate(http_request_duration_seconds_bucket{app=~".*-backend"}[5m])
  )
)

# Запросов по endpoint'ам
topk(10, sum by (endpoint) (rate(http_requests_total[1h])))
```

## 🚀 Как это работает

1. **Prometheus** каждые 30 секунд опрашивает `/metrics` endpoint
2. **Backend** генерирует метрики в текстовом формате
3. **Prometheus** сохраняет метрики в свою TSDB (Time Series Database)
4. **Grafana** запрашивает данные из Prometheus и показывает на дашборде

## 📝 Пример метрик

После нескольких запросов к backend'ам:

```
# Метрики процесса (автоматически от prometheus_client)
process_cpu_seconds_total 12.5
process_resident_memory_bytes 125000000
process_open_fds 45

# HTTP метрики (наши кастомные)
http_requests_total{method="GET",endpoint="/api/v1/admin/foods/",status="200"} 150
http_requests_total{method="POST",endpoint="/api/v1/admin/dishes/",status="201"} 25
http_requests_total{method="GET",endpoint="/api/v1/admin/foods/",status="500"} 2

# Время выполнения
http_request_duration_seconds_sum{method="GET",endpoint="/api/v1/admin/foods/"} 7.5
http_request_duration_seconds_count{method="GET",endpoint="/api/v1/admin/foods/"} 150
```

## 🎯 Что мониторить

### Обязательно:
- ✅ **up** - статус backend'а
- ✅ **http_requests_total** - количество запросов
- ✅ **http_request_duration_seconds** - время ответа

### Процесс:
- ✅ **process_cpu_seconds_total** - CPU usage
- ✅ **process_resident_memory_bytes** - память
- ✅ **process_open_fds** - открытые файлы

### Ошибки:
- ⚠️ **http_requests_total{status=~"5.."}** - серверные ошибки
- ⚠️ **http_requests_total{status=~"4.."}** - клиентские ошибки

## 📊 Дашборд

Дашборд "Healthy Menu - Метрики Backend'ов" в Grafana уже настроен и показывает:
1. Backend Status (UP/DOWN)
2. CPU Usage
3. Memory Usage
4. Open File Descriptors
5. HTTP Request Duration

## 🔄 Обновление backend'ов

После изменения кода нужно:
```bash
# Пересобрать образы
docker build -t nexus:5000/admin-backend:latest ./admin-backend
docker build -t nexus:5000/order-backend:latest ./order-backend  
docker build -t nexus:5000/courier-backend:latest ./courier-backend

# Запушить в registry
docker push nexus:5000/admin-backend:latest
docker push nexus:5000/order-backend:latest
docker push nexus:5000/courier-backend:latest

# Обновить deployment'ы в K8s
kubectl rollout restart deployment -n healthy-menu-dev admin-backend
kubectl rollout restart deployment -n healthy-menu-dev order-backend
kubectl rollout restart deployment -n healthy-menu-dev courier-backend
```

## 🧪 Тестирование

```bash
# Проверка /metrics endpoint
kubectl port-forward -n healthy-menu-dev admin-backend-xxxxx 8000:8000
curl http://localhost:8000/metrics

# Генерация тестовых запросов
for i in {1..100}; do
  curl -s http://healthy-menu.local:32096/admin/api/v1/admin/foods/ > /dev/null
done

# Проверка что метрики появились
kubectl port-forward -n logging svc/prometheus-server 9090:80
curl 'http://localhost:9090/api/v1/query?query=http_requests_total' | jq
```
