# Loki + Promtail + Grafana - Краткая инструкция

## 🚀 Быстрая установка

```bash
# Создаём namespace
kubectl create namespace logging

# Добавляем репозиторий Grafana
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Устанавливаем все компоненты в namespace logging
helm install loki grafana/loki \
  --namespace logging \
  -f logging/loki-values.yaml

helm install grafana grafana/grafana \
  --namespace logging \
  -f logging/grafana-values.yaml

helm install promtail grafana/promtail \
  --namespace logging \
  -f logging/promtail-values.yaml

# Проверяем статус
kubectl get pods -n logging
```

## 🔗 Доступ к Grafana

```bash
# Порт-форвардинг
kubectl port-forward svc/grafana -n logging 3000:80

# Открываем браузер: http://localhost:3000
# Логин: admin
# Пароль: admin123
```

## 🔍 Тестирование работы

```bash
# Порт-форвардинг к Loki
kubectl port-forward svc/loki-gateway -n logging 3100:80

# Проверяем что Loki принимает логи
curl -H "X-Scope-OrgId: healthy-menu-dev" \
  http://localhost:3100/loki/api/v1/labels | jq

# Проверяем что backend'ы отправляют логи
curl -H "X-Scope-OrgId: healthy-menu-dev" \
  http://localhost:3100/loki/api/v1/label/app/values | jq

# Проверяем логи конкретного backend
curl -H "X-Scope-OrgId: healthy-menu-dev" \
  -G http://localhost:3100/loki/api/v1/query_range \
  --data-urlencode 'query={app="admin-backend"}' \
  --data-urlencode 'start=now-1h' \
  --data-urlencode 'end=now' | jq
```

## 📊 Работа с Grafana

1. Открой **Explore** (иконка компаса)
2. Выбери datasource **Loki**
3. Введи запрос: `{namespace="healthy-menu-dev", app="admin-backend"}`
4. Нажми **Run query**

### Примеры LogQL запросов

```logql
# Все логи backend'ов
{namespace="healthy-menu-dev", app=~".*-backend"}

# Только ошибки
{namespace="healthy-menu-dev", level="ERROR"}

# Логи по конкретному pod
{namespace="healthy-menu-dev", pod="admin-backend-xxxxx"}

# Агрегация по уровням
sum by (level) (count_over_time({namespace="healthy-menu-dev"}[1h]))
```

## 🔧 Полезные команды

```bash
# Проверка статуса
kubectl get pods -n logging
kubectl get daemonset -n logging promtail

# Логи компонентов
kubectl logs -n logging -l app.kubernetes.io/name=loki -f
kubectl logs -n logging -l app.kubernetes.io/name=promtail -f
kubectl logs -n logging -l app.kubernetes.io/name=grafana -f

# Перезапуск компонентов
kubectl rollout restart statefulset/loki -n logging
kubectl rollout restart deployment/grafana -n logging
kubectl rollout restart daemonset/promtail -n logging
```

## 🗑️ Удаление

```bash
# Удаление всех компонентов
helm uninstall promtail -n logging
helm uninstall grafana -n logging
helm uninstall loki -n logging

# Удаление PVC
kubectl delete pvc -n logging -l app.kubernetes.io/name=loki

# Удаление namespace
kubectl delete namespace logging
```

## 📁 Файлы конфигурации

- `loki-values.yaml` - конфигурация Loki
- `grafana-values.yaml` - конфигурация Grafana
- `promtail-values.yaml` - конфигурация Promtail

## ⚠️ Важно

Grafana datasource настроен с tenant header `X-Scope-OrgId: healthy-menu-dev`. 
При ручном создании datasource обязательно укажите:
- **HTTP Headers**: `X-Scope-OrgId`
- **Value**: `healthy-menu-dev`
