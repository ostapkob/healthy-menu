terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
  required_version = ">= 1.0.0"
}

# Провайдер Docker
provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# Общая сеть для всех сервисов
# resource "docker_network" "app_network" {
#   name   = "app-network"
#   driver = "bridge"

#   ipam_config {
#     subnet = "172.21.0.0/24" # Изменён подсеть для избежания конфликтов
#   }

#   # Не давать сети удаляться, пока есть контейнеры
#   lifecycle {
#     create_before_destroy = true
#     prevent_destroy       = false # Можно временно поставить true для отладки
#   }
# }


# ==================== PostgreSQL ====================
resource "docker_volume" "postgres_data" {
  name = "postgres_data"
}

resource "docker_image" "postgres" {
  name         = "postgres:16-alpine"
  keep_locally = true
}

resource "docker_container" "postgres" {
  name    = "postgres"
  image   = docker_image.postgres.image_id
  restart = "always"

  env = [
    "POSTGRES_HOST=${var.postgres_host}",
    "POSTGRES_PORT=${var.postgres_port}",
    "POSTGRES_USER=${var.postgres_user}",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=${var.postgres_db}"
  ]

  ports {
    internal = 5432
    external = 5432
    ip       = "0.0.0.0"
  }

  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
    read_only      = false
  }

  networks_advanced {
    name    = "app-network"
    aliases = ["postgres"]
  }

  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U ${var.postgres_user}"]
    interval = "5s"
    timeout  = "5s"
    retries  = 10
  }

  # Ограничение ресурсов
  cpu_shares = 512
  memory     = 1024 # 1GB
}

# ==================== Zookeeper (для Kafka) ====================
resource "docker_image" "zookeeper" {
  name         = "confluentinc/cp-zookeeper:latest"
  keep_locally = true
}

resource "docker_container" "zookeeper" {
  name    = "zookeeper"
  image   = docker_image.zookeeper.image_id
  restart = "always"

  env = [
    "ZOOKEEPER_CLIENT_PORT=2181",
    "ZOOKEEPER_TICK_TIME=2000"
  ]

  ports {
    internal = 2181
    external = 2181
    ip       = "0.0.0.0"
  }

  networks_advanced {
    name    = "app-network"
    aliases = ["zookeeper"]
  }

  healthcheck {
    test     = ["CMD", "bash", "-c", "echo ruok | nc localhost 2181"]
    interval = "10s"
    timeout  = "5s"
    retries  = 5
  }

  cpu_shares = 256
  memory     = 512 # 512MB
}

# ==================== Kafka ====================
resource "docker_image" "kafka" {
  name         = "confluentinc/cp-kafka:7.4.0"
  keep_locally = true
}

resource "docker_container" "kafka" {
  name       = "kafka"
  image      = docker_image.kafka.image_id
  restart    = "always"
  depends_on = [docker_container.zookeeper]

  env = [
    "KAFKA_BROKER_ID=1",
    "KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181",
    "KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092",
    "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT",
    "KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT",
    "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1",
    "KAFKA_AUTO_CREATE_TOPICS_ENABLE=true",
    "KAFKA_NUM_PARTITIONS=3"
  ]

  ports {
    internal = 9092
    external = 9092
    ip       = "0.0.0.0"
  }

  networks_advanced {
    name    = "app-network"
    aliases = ["kafka"]
  }

  healthcheck {
    test     = ["CMD", "kafka-topics", "--bootstrap-server", "localhost:9092", "--list"]
    interval = "15s"
    timeout  = "10s"
    retries  = 5
  }

  cpu_shares = 512
  memory     = 1024 # 1GB
}

# ==================== MinIO ====================
resource "docker_volume" "minio_data" {
  name = "minio_data"
}

resource "docker_image" "minio" {
  name         = "quay.io/minio/minio:latest"
  keep_locally = true
}

resource "docker_container" "minio" {
  name    = "minio"
  image   = docker_image.minio.image_id
  restart = "always"

  env = [
    "MINIO_ROOT_USER=${var.minio_root_user}",
    "MINIO_ROOT_PASSWORD=${var.minio_root_password}"
  ]

  command = ["server", "/data", "--console-address", ":9001"]

  ports {
    internal = 9000
    external = 9000
    ip       = "0.0.0.0"
  }

  ports {
    internal = 9001
    external = 9001
    ip       = "0.0.0.0"
  }

  volumes {
    volume_name    = docker_volume.minio_data.name
    container_path = "/data"
    read_only      = false
  }

  networks_advanced {
    name    = "app-network"
    aliases = ["minio"]
  }

  healthcheck {
    test     = ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
    interval = "5s"
    timeout  = "5s"
    retries  = 5
  }

  cpu_shares = 512
  memory     = 1024 # 1GB
}

# ==================== Инициализация MinIO ====================
resource "docker_image" "mc" {
  name         = "quay.io/minio/mc:latest"
  keep_locally = true
}

# Временный контейнер для инициализации MinIO
resource "docker_container" "minio_init" {
  name    = "minio-init"
  image   = docker_image.mc.image_id
  restart = "no"

  # Переопределяем entrypoint на /bin/sh
  entrypoint = ["/bin/sh", "-c"]

  # Команда для выполнения
  command = [<<-EOT
    echo "Waiting for MinIO to be ready..."

    # ждать пока mc сможет подключиться к серверу
    until /usr/bin/mc admin info minio >/dev/null 2>&1; do
      /usr/bin/mc alias set minio http://minio:9000 ${var.minio_root_user} ${var.minio_root_password} >/dev/null 2>&1 || true
      sleep 2
    done

    echo "Setting up MinIO alias..."
    /usr/bin/mc alias set minio http://minio:9000 ${var.minio_root_user} ${var.minio_root_password}

    echo "Creating bucket '${var.minio_bucket}'..."
    /usr/bin/mc mb minio/${var.minio_bucket} --ignore-existing

    echo "Setting bucket policy to public..."
    /usr/bin/mc anonymous set public minio/${var.minio_bucket}

    echo "Listing buckets to verify..."
    /usr/bin/mc ls minio/

    echo "MinIO initialization complete!"
    EOT
  ]

  networks_advanced {
    name = "app-network"
  }

  # Зависит от основного контейнера MinIO
  depends_on = [docker_container.minio]

  # Удаляем контейнер после выполнения (очистка)
  rm = true
}


# ==================== Тестовый продюсер Kafka ====================
# resource "null_resource" "kafka_test" {
#   depends_on = [docker_container.kafka]
#
#   provisioner "local-exec" {
#     command = <<-EOT
#       echo "Waiting for Kafka..."
#       sleep 20
#
#       echo "Creating test topic..."
#       docker run --rm --network ${docker_network.app_network.name} \
#         confluentinc/cp-kafka:7.4.0 \
#         kafka-topics --bootstrap-server kafka:9092 \
#         --create --topic test-topic --partitions 1 --replication-factor 1 --if-not-exists
#
#       echo "Sending test message..."
#       docker run --rm --network ${docker_network.app_network.name} \
#         confluentinc/cp-kafka:7.4.0 \
#         bash -c 'echo "{\"message\": \"Terraform deployment successful!\"}" | \
#         kafka-console-producer --bootstrap-server kafka:9092 --topic test-topic'
#
#       echo "Test message sent!"
#     EOT
#   }
#
#   triggers = {
#     always_run = timestamp()
#   }
# }
#

# ==================== Nexus ====================
resource "docker_volume" "nexus_data" {
  name = "nexus_data"
}

resource "docker_image" "nexus" {
  name         = "sonatype/nexus3:latest"
  keep_locally = true
}

resource "docker_container" "nexus" {
  name    = "nexus"
  image   = docker_image.nexus.image_id
  restart = "unless-stopped"

  ports {
    internal = 8081
    external = var.nexus_host_port
  }

  ports {
    internal = 5000
    external = var.nexus_registry_port
  }

  volumes {
    volume_name    = docker_volume.nexus_data.name
    container_path = "/nexus-data"
  }

  networks_advanced {
    name    = "app-network"
    aliases = ["nexus"]
  }

  healthcheck {
    test     = ["CMD", "curl", "-f", "http://localhost:8081/"]
    interval = "30s"
    timeout  = "10s"
    retries  = 5
  }

  # lifecycle {
  #   prevent_destroy = true
  # }

  # Nexus требует больше памяти
  cpu_shares  = 1024
  memory      = 2048 # 2GB минимум для Nexus
  memory_swap = 4096
}


# ==================== GitLab ====================
resource "docker_volume" "gitlab_config" {
  name = "gitlab_config"
}
resource "docker_volume" "gitlab_logs" {
  name = "gitlab_logs"
}
resource "docker_volume" "gitlab_data" {
  name = "gitlab_data"
}
resource "docker_image" "gitlab" {
  name         = "gitlab/gitlab-ce:latest"
  keep_locally = true
}
resource "docker_container" "gitlab" {
  name    = "gitlab"
  image   = docker_image.gitlab.image_id
  restart = "always"
  ports {
    internal = 80
    external = var.gitlab_http_port
    ip       = "0.0.0.0"
  }
  ports {
    internal = 22
    external = var.gitlab_ssh_port
    ip       = "0.0.0.0"
  }
  volumes {
    volume_name    = docker_volume.gitlab_config.name
    container_path = "/etc/gitlab"
  }
  volumes {
    volume_name    = docker_volume.gitlab_logs.name
    container_path = "/var/log/gitlab"
  }
  volumes {
    volume_name    = docker_volume.gitlab_data.name
    container_path = "/var/opt/gitlab"
  }
  # shared memory (256mb)
  shm_size = 1024 * 1024 * 256
  networks_advanced {
    name    = "app-network"
    aliases = ["gitlab"]
  }
  env = [
    <<EOT
GITLAB_OMNIBUS_CONFIG=<<-INNER
  external_url 'http://localhost:${var.gitlab_http_port}'
  gitlab_rails['gitlab_shell_ssh_port'] = ${var.gitlab_ssh_port}
  nginx['listen_port'] = 80
  nginx['listen_https'] = false
  nginx['proxy_set_headers'] = { "Host" => "localhost:${var.gitlab_http_port}" }
  gitlab_rails['time_zone'] = 'UTC'
INNER
EOT
  ]
  cpu_shares  = 2048
  memory      = var.gitlab_memory_limit * 1024 * 1024
  memory_swap = var.gitlab_memory_limit * 1024 * 1024 * 2
  healthcheck {
    test         = ["CMD-SHELL", "curl --fail --silent http://localhost/-/health || exit 1"]
    interval     = "30s"
    timeout      = "10s"
    retries      = 8
    start_period = "300s"
  }
}

# ==================== SonarQube PostgreSQL ====================
resource "docker_volume" "postgres_sonar_data" {
  name = "postgres-sonar-data"
}

resource "docker_image" "postgres_sonar" {
  name         = "postgres:13-alpine"
  keep_locally = true
}

resource "docker_container" "postgres_sonar" {
  name    = "postgres-sonar"
  image   = docker_image.postgres_sonar.image_id
  restart = "unless-stopped"

  env = [
    "POSTGRES_USER=${var.sonar_postgres_user}",
    "POSTGRES_PASSWORD=${var.sonar_postgres_password}",
    "POSTGRES_DB=${var.sonar_postgres_db}"
  ]

  volumes {
    volume_name    = docker_volume.postgres_sonar_data.name
    container_path = "/var/lib/postgresql/data"
  }

  networks_advanced {
    name    = "app-network"
    aliases = ["postgres-sonar"]
  }

  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U ${var.sonar_postgres_user}"]
    interval = "10s"
    timeout  = "5s"
    retries  = 5
  }

  cpu_shares = 256
  memory     = 512 # 512MB
}

# ==================== SonarQube ====================
resource "docker_volume" "sonarqube_data" {
  name = "sonarqube_data"
}

resource "docker_image" "sonarqube" {
  name         = "sonarqube:lts-community"
  keep_locally = true
}

resource "docker_container" "sonarqube" {
  name       = "sonarqube"
  image      = docker_image.sonarqube.image_id
  restart    = "unless-stopped"
  depends_on = [docker_container.postgres_sonar]

  env = [
    "SONAR_JDBC_URL=jdbc:postgresql://postgres-sonar:5432/${var.sonar_postgres_db}",
    "SONAR_JDBC_USERNAME=${var.sonar_postgres_user}",
    "SONAR_JDBC_PASSWORD=${var.sonar_postgres_password}",
    "SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=${var.sonar_es_disable_bootstrap_checks}"
  ]

  ports {
    internal = 9000
    external = var.sonar_web_port
    ip       = "0.0.0.0"
  }

  volumes {
    volume_name    = docker_volume.sonarqube_data.name
    container_path = "/opt/sonarqube/data"
  }

  networks_advanced {
    name    = "app-network"
    aliases = ["sonarqube"]
  }

  healthcheck {
    # Проверяем, что в ответе есть статус "UP"
    test         = ["CMD-SHELL", "wget -qO- http://localhost:9000/api/system/status | grep -q 'UP' || exit 1"]
    interval     = "30s"
    timeout      = "10s"
    retries      = 10
    start_period = "120s"
  }
  cpu_shares  = 1024 # 1 ядро
  memory      = 2048 # 2GB минимум для SonarQube
  memory_swap = 4096
}


# ==================== Jenkins ====================

resource "docker_volume" "jenkins_home" {
  name = "jenkins_home"
}

resource "docker_image" "jenkins" {
  name         = "jenkins/jenkins:lts"
  keep_locally = true
}

resource "docker_container" "jenkins" {
  name    = "jenkins"
  image   = docker_image.jenkins.image_id
  restart = "always"

  ports {
    internal = 8080
    external = 8080
    ip       = "0.0.0.0"
  }
  ports {
    internal = 50000
    external = 50000
    ip       = "0.0.0.0"
  }
  volumes {
    volume_name    = docker_volume.jenkins_home.name
    container_path = "/var/jenkins_home"
  }
  env = [
    "JENKINS_OPTS=--httpPort=8080"
  ]
  networks_advanced {
    name    = "app-network"
    aliases = ["jenkins"]
  }
  healthcheck {
    test         = ["CMD-SHELL", "bash -c ':> /dev/tcp/127.0.0.1/8080' || exit 1"]
    interval     = "30s"
    timeout      = "10s"
    retries      = 5
    start_period = "90s"
  }
  # Ресурсы как в твоих контейнерах
  cpu_shares = 1024
  memory     = 2048 # 2GB
}


# ==================== Jenkins-Agent ====================
resource "docker_volume" "agent_docker_cache" {
  name = "jenkins_agent_docker_data"
}

resource "docker_volume" "jenkins_uv_cache" {
  name = "jenkins_uv_cache"
}

resource "docker_container" "jenkins_agent" {
  name       = "jenkins-agent"
  image      = "jenkins/inbound-agent:alpine"
  privileged = true
  user       = "root" # Нужно для запуска docker daemon внутри

  memory     = 4096
  cpu_shares = 2048

  depends_on = [docker_container.jenkins, docker_container.postgres, docker_container.kafka, docker_container.minio]

  # FIX: use hashicorp vault
  env = [
    "JENKINS_URL=http://jenkins:8080",
    "JENKINS_SECRET=3001527dbd2b351f03f6327ca215ac9752816a219b24322dcfbf8d706d3ef25d",
    "JENKINS_AGENT_NAME=agent-1",
    "JENKINS_WEB_SOCKET=true",
    "POSTGRES_HOST=${var.postgres_host}",
    "POSTGRES_PORT=${var.postgres_port}",
    "POSTGRES_USER=${var.postgres_user}",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=${var.postgres_db}",
    "MINIO_ROOT_USER=${var.minio_root_user}",
    "MINIO_ROOT_PASSWORD=${var.minio_root_password}",
    "MINIO_BUCKET=${var.minio_bucket}",
    "MINIO_HOST=${var.minio_host}",
    "MINIO_PORT=${var.minio_port}",
    "MINIO_IP=${docker_container.minio.network_data[0].ip_address}",
    "POSTGRES_IP=${docker_container.postgres.network_data[0].ip_address}",
    "KAFKA_IP=${docker_container.kafka.network_data[0].ip_address}",
    "SONAR_IP=${docker_container.sonarqube.network_data[0].ip_address}",
    "NEXUS_REGISTRY_URL=${docker_container.nexus.name}:${var.nexus_registry_port}"
  ]

  # FIX: after https rm insecure
  entrypoint = [
    "sh", "-c",
    <<-EOT
    if ! command -v docker >/dev/null; then
      apk add --no-cache docker fuse-overlayfs jq curl
      rm -f /var/run/docker.pid /var/run/docker.sock
    fi
    (dockerd --storage-driver=fuse-overlayfs \
      --host=unix:///var/run/docker.sock \
      --insecure-registry nexus:5000 \
      --insecure-registry localhost:5000 \
      --insecure-registry ${docker_container.nexus.network_data[0].ip_address}:${var.nexus_registry_port} &) && \
    sleep 5
    /usr/local/bin/jenkins-agent
    EOT
  ]


  volumes {
    volume_name    = docker_volume.agent_docker_cache.name
    container_path = "/var/lib/docker"
  }

  volumes {
    volume_name    = "jenkins_uv_cache"
    container_path = "/root/.cache/uv"
  }

  networks_advanced {
    name    = "app-network"
    aliases = ["postgres-sonar"]
  }

  healthcheck {
    test         = ["CMD-SHELL", "docker version >/dev/null 2>&1 || exit 1"]
    interval     = "30s"
    timeout      = "10s"
    retries      = 5
    start_period = "90s"
  }

}


resource "terraform_data" "bootstrap" {
  # Список зависимостей
  depends_on = [
    docker_container.jenkins,
    docker_container.postgres,
    docker_container.nexus,
    docker_container.minio,
    docker_container.gitlab,
    docker_container.sonarqube
  ]

  provisioner "local-exec" {
    # Указываем папку, где лежат ваши Makefile, вместо "cd .."
    working_dir = "${path.module}/.."

    command = <<EOT
      # Функция ожидания здоровья контейнера
      wait_for_healthy() {
        echo "Waiting for $1 to be healthy..."
        until [ "$(docker inspect --format='{{.State.Health.Status}}' $1)" == "healthy" ]; do
          sleep 5
        done
      }

      # Ждем самые тяжелые сервисы
      wait_for_healthy "${docker_container.gitlab.name}"
      wait_for_healthy "${docker_container.nexus.name}"
      wait_for_healthy "${docker_container.sonarqube.name}"

      # Запуск основной логики
      make setup-models
      make load-data
      make setup-nexus
      make setup-sonar
      make setup-gitlab
      echo "Done 🍾🍾🍾"
    EOT
  }
}
