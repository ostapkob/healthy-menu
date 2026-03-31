# Prometheus + Grafana - Краткая инструкция

## 🚀 Что установлено

| Компонент | Namespace | Назначение |
|-----------|-----------|------------|
| **Prometheus** | `logging` | Сбор и хранение метрик |
| **Grafana** | `logging` | Визуализация метрик и логов |
| **kube-state-metrics** | `logging` | Метрики Kubernetes объектов |
| **node-exporter** | `logging` | Метрики нод |
| **pushgateway** | `logging` | Push метрики |

## 🔗 Доступ к Grafana

```bash
# Порт-форвардинг
kubectl port-forward svc/grafana -n logging 3000:80

# Открываем браузер: http://localhost:3000
# Логин: admin
# Пароль: admin123
```

## 📊 Дашборды

### Healthy Menu - Метрики Backend'ов
- **URL**: `/d/healthy-menu-metrics/healthy-menu-metriki-backend-ov`
- **Метрики**:
  - Backend Status (UP/DOWN)
  - CPU Usage
  - Memory Usage
  - Open File Descriptors
  - HTTP Request Duration

### Healthy Menu - Логи Backend'ов (если Loki установлен)
- **URL**: `/d/healthy-menu-logs/healthy-menu-logi-backend-ov`

## 🔍 Prometheus Query примеры

```promql
# Статус backend'ов
up{app=~".*-backend"}

# Потребление CPU
rate(process_cpu_seconds_total{app=~".*-backend"}[5m])

# Потребление памяти
process_resident_memory_bytes{app=~".*-backend"}

# Открытые файловые дескрипторы
process_open_fds{app=~".*-backend"}

# Среднее время HTTP запроса
rate(http_request_duration_seconds_sum{app=~".*-backend"}[5m]) / 
rate(http_request_duration_seconds_count{app=~".*-backend"}[5m])
```

## 📁 Файлы конфигурации

- `monitoring/prometheus-values.yaml` - конфигурация Prometheus
- `monitoring/healthy-menu-dashboard.json` - дашборд Grafana
- `gitops/services/*-backend.yaml` - аннотации Prometheus для backend'ов

## ⚙️ Как Prometheus собирает метрики

1. Backend'ы имеют аннотации:
   ```yaml
   annotations:
     prometheus.io/scrape: "true"
     prometheus.io/port: "8000"
     prometheus.io/path: "/metrics"
   ```

2. Prometheus сканирует поды в `healthy-menu-dev` namespace
3. Собирает метрики с портов указанных в аннотациях
4. Добавляет метки: `namespace`, `pod`, `app`

## 🔧 Полезные команды

```bash
# Проверка targets Prometheus
kubectl port-forward svc/prometheus-server -n logging 9090:80
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | .labels.job'

# Проверка доступных метрик
curl http://localhost:9090/api/v1/label/__name__/values | jq '.data[]'

# Query метрик
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up{app="admin-backend"}' | jq
```

## 🗑️ Удаление

```bash
# Удаление Prometheus
helm uninstall prometheus -n logging

# Удаление Grafana
helm uninstall grafana -n logging

# Удаление PVC
kubectl delete pvc -n logging -l app.kubernetes.io/name=prometheus
kubectl delete pvc -n logging grafana
```
