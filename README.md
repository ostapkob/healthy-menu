# Healthy Menu 🍽️

Микросервисная платформа для управления меню с полноценным CI/CD циклом и GitOps подходом.

## 📋 О проекте

Система состоит из:
- **3 бэкенд-сервисов** (FastAPI/Python 3.13+)
- **3 фронтенд-сервисов**
- **Инфраструктуры**: PostgreSQL, Kafka, MinIO
- **CI/CD**: GitLab, Jenkins, SonarQube, Nexus, ArgoCD
- **Kubernetes**: развёртывание через Helm + ArgoCD GitOps
- **IaC**: Terraform для управления инфраструктурой

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    ArgoCD (GitOps)                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │    Admin     │  │    Order     │  │   Courier    │           │
│  │   Backend    │  │   Backend    │  │   Backend    │           │
│  │   (FastAPI)  │  │   (FastAPI)  │  │   (FastAPI)  │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
├───────────────────────────┼─────────────────────────────────────│
│                           │            infra                    │
│                    ┌──────▼───────┐                             │
│                    │   PostgreSQL │                             │
│                    └──────────────┘                             │
│                           │                                     │
│                    ┌──────▼───────┐                             │
│                    │    Kafka     │                             │
│                    └──────────────┘                             │
│                           │                                     │
│                    ┌──────▼───────┐                             │
│                    │    MinIO     │                             │
│                    └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         CI/CD Pipeline                          │
│                                                                 │
│  GitLab → Jenkins → SonarQube  →  Nexus   → ArgoCD → K8s        │
│  (code)   (build)   (analysis)  (registry) (deploy) (run)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Быстрый старт

### Предварительные требования

- Docker & Docker Compose
- Terraform >= 1.0.0 с провайдерами `docker` и `null`
- Python 3.13+ с `uv` или `pip`
- Для Kubernetes: `kubectl`, `helm`, `argocd`, `istioctl` CLI

### 1. Клонирование и настройка

```bash
git clone <your-repo-url>
cd healthy-menu

# Создайте .env файлы из примера
cp env_example .env
cp env_example admin-backend/.env
cp env_example order-backend/.env
cp env_example courier-backend/.env
cp env_example terraform/.env
```

---

## 🐳 Вариант 1: Docker Compose (локальная разработка)

### Запуск инфраструктуры

```bash
# Запуск инфраструктуры (PostgreSQL, Kafka, MinIO)
docker-compose --profile infra up -d

# Запуск бэкенд и фронтенд сервисов
docker-compose --profile back_front up -d

# Просмотр логов
docker-compose logs -f
```

### Остановка

```bash
docker-compose --profile infra down
# или полностью очистить всё
docker-compose --profile infra down -v
```

---

## 🏗️ Вариант 2: Terraform (продакшен-подобное окружение)

**Это основной способ развёртывания инфраструктуры.** Вся инфраструктура управляется через Terraform, что обеспечивает идемпотентность, версионирование состояния и автоматическую настройку всех сервисов.

### Предварительные требования

```bash
cd terraform
terraform init

⚠️ в России 🇷🇺 проблемма с установкой поэтому используем [ссылку]( https://yandex.cloud/ru/docs/tutorials/infrastructure-management/terraform-quickstart#linux_1 ) на yandex
```

### Развёртывание

```bash
# Применение всей конфигурации
terraform apply -auto-approve

# Применение с просмотром плана
terraform plan
terraform apply
```

### Работа с отдельными ресурсами

```bash
# Перезапуск конкретного контейнера (например, Jenkins Agent)
terraform apply -target=docker_container.jenkins_agent -auto-approve

# Пересоздание ресурса
terraform apply -target=docker_container.jenkins_agent \
  -replace=docker_container.jenkins_agent \
  -auto-approve

# Удаление ресурса
terraform destroy -target=docker_container.jenkins_agent -auto-approve
```

### Очистка и пересоздание Nexus

```bash
# Удаление состояния Nexus
terraform state rm null_resource.nexus_init

# Остановка и удаление контейнера
docker stop nexus
docker rm nexus
docker volume rm nexus_data

# Применение заново
terraform apply -auto-approve
```

### Полезные команды Terraform

```bash
# Просмотр состояния
terraform state list

# Просмотр конкретного ресурса
terraform state show docker_container.postgres

# Импорт существующего ресурса
terraform import docker_volume.postgres_data postgres_data

# Форматирование
terraform fmt -recursive

# Валидация
terraform validate
```

### Выходные данные (Outputs)

После применения Terraform выведет информацию о подключении:

```bash
# MinIO
terraform output minio_connection

# Kafka
terraform output kafka_connection

# GitLab
terraform output gitlab_connection

# Nexus
terraform output nexus_connection

# SonarQube
terraform output sonarqube_connection
```

### Автоматическая инициализация

После развёртывания инфраструктуры Terraform автоматически выполнит:
- Ожидание готовности всех сервисов
- Инициализацию моделей БД (`make setup-models`)
- Загрузку тестовых данных (`make load-data`)
- Настройку Nexus (`make setup-nexus`)
- Настройку SonarQube (`make setup-sonar`)
- Настройку GitLab (`make setup-gitlab`)

---

## 🔀 Сравнение подходов

| Характеристика | Docker Compose | Terraform |
|----------------|----------------|-----------|
| **Назначение** | Локальная разработка | Продакшен-подобное окружение |
| **Управление состоянием** | Нет | Есть (state file) |
| **Идемпотентность** | Частичная | Полная |
| **Автоматическая настройка** | Нет | Да (bootstrap) |
| **Работа с отдельными сервисами** | `docker-compose up -d <service>` | `-target` флаг |
| **Сложность** | Низкая | Средняя |

> 💡 **Рекомендация**: Используйте Docker Compose для быстрой локальной разработки и Terraform для развёртывания полноценного CI/CD окружения.

---

## ⚠️ Важные замечания

### Конфликты портов

Docker Compose и Terraform используют **одинаковые порты**, поэтому **нельзя запускать одновременно**:

```bash
# Остановите Docker Compose перед запуском Terraform
docker-compose --profile infra down

# Или остановите Terraform перед запуском Docker Compose
terraform destroy -auto-approve
```

### Совместимость данных

✅ **Docker Compose и Terraform используют одинаковые имена volume** — данные будут общими при переключении между подходами.

| Ресурс | Volume имя |
|--------|------------|
| PostgreSQL | `postgres_data` |
| MinIO | `minio_data` |
| Nexus | `nexus_data` |
| Jenkins | `jenkins_home` |
| SonarQube | `sonarqube_data` |
| Sonar PostgreSQL | `postgres_sonar_data` |

### Сетевые алиасы

Оба подхода используют сеть `app-network` с алиасами для сервисов (`postgres`, `kafka`, `minio`), 
что позволяет сервисам обращаться друг к другу по имени.

---

## 📍 Доступ к сервисам

| Сервис | Порт | URL | Описание |
|--------|------|-----|----------|
| Admin Backend | 8001 | http://localhost:8001 | FastAPI админка |
| Order Backend | 8002 | http://localhost:8002 | FastAPI заказы |
| Courier Backend | 8003 | http://localhost:8003 | FastAPI курьеры |
| Admin Frontend | 3001 | http://localhost:3001 | UI админки |
| Order Frontend | 3002 | http://localhost:3002 | UI заказов |
| Courier Frontend | 3003 | http://localhost:3003 | UI курьеров |
| PostgreSQL | 5432 | localhost:5432 | База данных |
| Kafka | 9092 | localhost:9092 | Message broker |
| MinIO UI | 9001 | http://localhost:9001 | S3-хранилище |
| GitLab | 8060 | http://localhost:8060 | Git repository |
| Jenkins | 8080 | http://localhost:8080 | CI/CD пайплайны |
| SonarQube | 9009 | http://localhost:9009 | Code analysis |
| Nexus | 8081 | http://localhost:8081 | Artifact registry |
| Nexus Registry | 5000 | localhost:5000 | Docker registry |

---

## 🛠️ Разработка

### Бэкенд

```bash
# Перейдите в директорию сервиса
cd admin-backend

# Установка зависимостей (uv)
uv sync

# Запуск сервера разработки
uv run uvicorn main:app --reload --port 8002

# Запуск тестов
uv run pytest tests -v

# Запуск с покрытием
uv run pytest tests -v --cov=api --cov-report=html
```

### Фронтенд

```bash
cd admin-frontend
npm install
npm run dev
```

### Полезные команды (Makefile)

```bash
make load-data          # Загрузка тестовых данных из CSV
make setup-models       # Инициализация моделей БД (Alembic)
make jenkins-backup     # Очистка backup Jenkins для переноса
make publish            # Публикация образов в registry
make push-gitlab        # Push кода в GitLab
make setup-gitlab       # Настройка GitLab
make setup-nexus        # Настройка Nexus
make setup-sonar        # Настройка SonarQube
```

### Работа с базой данных

```bash
# Установка csvkit для работы с CSV
pip install csvkit

# Инициализация моделей
make setup-models

# Загрузка тестовых данных
make load-data

# Создание тестовой БД
psql -U postgres -c "CREATE DATABASE food_db_tests WITH TEMPLATE food_db;"
```

### Kafka

```bash
# Список топиков
kafka-topics --bootstrap-server localhost:9092 --list

# Продюсер сообщений
kafka-console-producer --bootstrap-server localhost:9092 --topic new_orders

# Консьюмер сообщений
kafka-console-consumer --bootstrap-server localhost:9092 --topic new_orders --from-beginning

# Альтернативно через kcat
kcat -b kafka:9092 -t new_orders -C
```

### MinIO

```bash
# Доступ к UI
http://localhost:9001

# Логин: из .env (MINIO_ROOT_USER / MINIO_ROOT_PASSWORD)
# Bucket создаётся автоматически при запуске
```

---

## 📦 CI/CD

### Компоненты

| Компонент | Порт | Описание |
|-----------|------|----------|
| GitLab | 8060 | Репозиторий кода, вебхуки |
| Jenkins | 8080 | Пайплайны сборки и деплоя |
| SonarQube | 9009 | Статический анализ кода |
| Nexus | 8081/5000 | Артефакты и Docker registry |

### Запуск CI/CD стека

```bash
docker-compose --profile ci_cd up -d

# Просмотр начального пароля Jenkins
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# Настройка GitLab
make setup-gitlab
make push-gitlab
```

### Настройка GitLab вебхуков

1. Admin → Settings → Network → Outbound requests
2. ✅ Allow requests to the local network from webhooks and integrations
3. Добавьте Jenkins в whitelist

### Тестирование вебхука Jenkins

```bash
curl -v \
  -X POST \
  -H "Content-Type: application/json" \
  -H "X-Gitlab-Event: Merge Request Hook" \
  -d '{
    "object_kind": "merge_request",
    "event_type": "merge_request",
    "project": {"path_with_namespace": "ostapkob/admin-backend"},
    "object_attributes": {
      "action": "merged",
      "source_branch": "feature/test",
      "target_branch": "master"
    }
  }' \
  "http://jenkins:8080/generic-webhook-trigger/invoke?token=gitlab-mr-build"
```

### SonarQube
Скрипт ./scripts/setup-sonar.sh

пока убрать Coverage on New Code до 0%

Ручная настройка 
1. Логин: `admin` / `admin`
2. Создайте токен: My Account → Security → Global Analysis Token
3. Добавьте токен в Jenkins credentials
4. Настройте webhook: Administration → Configuration → Webhooks
   - URL: `http://jenkins:8080/sonarqube-webhook/`

---

## 🌐 Istio Service Mesh

### Интеграция с Helm и ArgoCD

Istio ресурсы генерируются автоматически через Helm chart при развёртывании через ArgoCD.

#### Какие Istio ресурсы создаются автоматически

| Ресурс | Шаблон | Описание |
|--------|--------|----------|
| DestinationRule | `infra/templates/destination-rule.yaml` | Circuit breaker, connection pool |
| PeerAuthentication | `infra/templates/peer-authentication.yaml` | mTLS настройки (PERMISSIVE/STRICT) |
| AuthorizationPolicy | `infra/templates/authorization-policy.yaml` | Правила доступа между сервисами |

#### Ручное применение (только Gateway)

Gateway и VirtualService применяются вручную, так как они глобальные для всех сервисов:

```bash
kubectl apply -f istio/gateway.yaml
```

### Проверка работы

```bash
# Проверка статуса proxy
istioctl proxy-status

# Проверка Gateway
kubectl get gateway -n healthy-menu-dev

# Проверка VirtualService
kubectl get virtualservice -n healthy-menu-dev

# Анализ конфигурации
istioctl analyze -n healthy-menu-dev
```


### Включение строгого mTLS (опционально)

Для продакшена рекомендуется включить mode STRICT для PeerAuthentication


---

## ☸️ Kubernetes

### Установка ArgoCD

```bash
# Запуск Minikube
minikube start --insecure-registry="nexus:5000"

# Создание namespace
kubectl create namespace argocd
kubectl create namespace healthy-menu-dev

# Установка ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Установка CRDs
curl -LO https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/crds/applicationset-crd.yaml
kubectl apply --server-side --force-conflicts -f applicationset-crd.yaml
rm applicationset-crd.yaml

# Проверка
kubectl get crd | grep argoproj.io

# Порт-форвардинг
kubectl port-forward --address localhost,192.168.1.163 svc/argocd-server -n argocd 18080:443

# Получение пароля
argocd admin initial-password -n argocd

# Логин
argocd login localhost:18080 --username admin --password $ARGO_PASSWORD --insecure
```

# Проверка 
helm template admin-backend ./infra --set istio.enabled=true -f gitops/services/admin-backend.yaml

### Добавление репозиториев в ArgoCD

```bash
# Infra репозиторий
argocd repo add http://gitlab:80/ostapkob/infra.git \
  --username git \
  --password $GITLAB_ACCESS_TOKEN \
  --name infra

# GitOps репозиторий
argocd repo add http://gitlab:80/ostapkob/gitops.git \
  --username git \
  --password $GITLAB_ACCESS_TOKEN \
  --name gitops
```

### Деплой приложений

```bash
# Применение ApplicationSet
kubectl apply -f gitops/argocd-appsets/dev-appset.yaml -n argocd

# Удаление (если нужно)
kubectl delete appset healthy-menu-dev -n argocd
```

### Istio (опционально)

```bash
# Установка Istio
curl -L https://istio.io/downloadIstio | sh -
istioctl install --set profile=default --skip-confirmation

# Включение injection для namespace
kubectl label namespace healthy-menu-dev istio-injection=enabled --overwrite

# Рестарт deployment'ов
kubectl rollout restart deployment -n healthy-menu-dev

# Применение Gateway и VirtualService
kubectl apply -f k8s/gateway.yaml
kubectl apply -f k8s/virtualservice.yaml
```

### Nexus в K8s

```bash
# Создание secret для pull образов
kubectl create secret docker-registry nexus-creds \
  --docker-server=nexus:5000 \
  --docker-username=ostapkob \
  --docker-password=superpass123 \
  --docker-email=any@example.com \
  -o yaml > nexus-secret.yaml
```

---

## 📂 Структура проекта

```
healthy-menu/
├── admin-backend/          # Бэкенд админ-панели (FastAPI)
├── order-backend/          # Бэкенд заказов (FastAPI)
├── courier-backend/        # Бэкенд курьеров (FastAPI)
├── admin-frontend/         # Фронтенд админ-панели
├── order-frontend/         # Фронтенд заказов
├── courier-frontend/       # Фронтенд курьеров
├── ci-pipelines/           # Jenkins pipeline скрипты (Groovy)
├── gitops/                 # ArgoCD манифесты
│   ├── argocd-appsets/     # ApplicationSet определения
│   └── services/           # Application для каждого сервиса
├── infra/                  # Helm чарты
│   ├── templates/          # Шаблоны Kubernetes + Istio
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── destination-rule.yaml    # Istio DestinationRule
│   │   ├── peer-authentication.yaml # Istio PeerAuthentication
│   │   └── authorization-policy.yaml # Istio AuthorizationPolicy
│   ├── Chart.yaml          # Метаданные чарта
│   └── values.yaml         # Значения по умолчанию (вкл. Istio)
├── k8s/                    # Kubernetes манифесты (legacy)
│   ├── gateway.yaml        # Istio Gateway (устарело)
│   └── virtualservice.yaml # Istio VirtualService (устарело)
├── scripts/                # Скрипты автоматизации
│   ├── cleanup_jenkins_backup.sh
│   ├── load-data.sh
│   ├── setup-gitlab.sh
│   └── ...
├── csv_data/               # CSV данные для загрузки в БД
├── istio/                  # Istio конфигурация (только Gateway)
│   └── gateway.yaml        # Gateway + VirtualService (маршрутизация)
├── jenkins/                # Jenkins агент
│   ├── Dockerfile          # Образ агента с Docker-in-Docker
│   └── jenkins_home/       # Домашняя директория Jenkins
├── terraform/              # Terraform конфигурация
│   ├── main.tf             # Основные ресурсы
│   ├── variables.tf        # Переменные
│   ├── outputs.tf          # Выходные данные
│   └── secrets.auto.tfvars # Секреты (в .gitignore)
├── docker-compose.yml      # Docker Compose для локальной разработки
├── Makefile                # Команды автоматизации
└── env_example             # Шаблон переменных окружения
```

---

## 🔧 Конфигурация

### Основные переменные окружения

Файл `.env` содержит настройки для всех сервисов:

```bash
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=food_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# MinIO (S3-compatible storage)
MINIO_HOST=localhost
MINIO_PORT=9000
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=password
MINIO_BUCKET=healthy-menu-dishes

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092

# GitLab
GITLAB_HOST=localhost
GITLAB_PORT=8060
GITLAB_ACCESS_TOKEN=<your-token>

# Jenkins
JENKINS_HOST=localhost
JENKINS_PORT=8080
JENKINS_SECRET=<agent-secret>

# SonarQube
SONAR_HOST=localhost
SONAR_PORT=9009
SONAR_TOKEN=<analysis-token>

# Nexus
NEXUS_HOST=localhost
NEXUS_PORT=8081
NEXUS_REGISTRY_PORT=5000
```

---

## 🔐 Безопасность

- Пароли по умолчанию измените в `.env` перед запуском
- Не коммитьте `.env` в репозиторий (добавлен в `.gitignore`)
- Для продакшена используйте Secrets Management (Vault, K8s Secrets)

---

## 📝 TODO

- [ ] HashiCorp Vault — управление секретами
- [ ] Istio — service mesh (частично реализован)
- [ ] FluentBit — централизованное логирование
- [ ] Prometheus + Grafana — мониторинг и алертинг
- [ ] HTTPS — TLS termination

---

## 📄 Лицензия

Pet project для обучения и экспериментов с микросервисной архитектурой и DevOps практиками.
