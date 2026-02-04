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
resource "docker_network" "app_network" {
  name   = "app-network"
  driver = "bridge"
  ipam_config {
    subnet = "172.21.0.0/24"  # Изменён подсеть для избежания конфликтов
  }
  
  # Не давать сети удаляться, пока есть контейнеры
  lifecycle {
    prevent_destroy = false  # Можно временно поставить true для отладки
  }
}

# # ==================== PostgreSQL ====================
# resource "docker_volume" "postgres_data" {
#   name = "postgres_data"
# }
#
# resource "docker_image" "postgres" {
#   name         = "postgres:16-alpine"
#   keep_locally = true
# }
#
# resource "docker_container" "postgres" {
#   name    = "postgres"
#   image   = docker_image.postgres.image_id
#   restart = "always"
#
#   env = [
#     "POSTGRES_USER=${var.postgres_user}",
#     "POSTGRES_PASSWORD=${var.postgres_password}",
#     "POSTGRES_DB=${var.postgres_db}"
#   ]
#
#   ports {
#     internal = 5432
#     external = 5432
#     ip       = "0.0.0.0"
#   }
#
#   volumes {
#     volume_name    = docker_volume.postgres_data.name
#     container_path = "/var/lib/postgresql/data"
#     read_only      = false
#   }
#
#   networks_advanced {
#     name    = docker_network.app_network.name
#     aliases = ["postgres"]
#   }
#
#   healthcheck {
#     test     = ["CMD-SHELL", "pg_isready -U ${var.postgres_user}"]
#     interval = "5s"
#     timeout  = "5s"
#     retries  = 10
#   }
#
#   # Ограничение ресурсов
#   cpu_shares = 512
#   memory     = 1024 # 1GB
# }
#
# # ==================== Zookeeper (для Kafka) ====================
# resource "docker_image" "zookeeper" {
#   name         = "confluentinc/cp-zookeeper:latest"
#   keep_locally = true
# }
#
# resource "docker_container" "zookeeper" {
#   name    = "zookeeper"
#   image   = docker_image.zookeeper.image_id
#   restart = "always"
#
#   env = [
#     "ZOOKEEPER_CLIENT_PORT=2181",
#     "ZOOKEEPER_TICK_TIME=2000"
#   ]
#
#   ports {
#     internal = 2181
#     external = 2181
#     ip       = "0.0.0.0"
#   }
#
#   networks_advanced {
#     name    = docker_network.app_network.name
#     aliases = ["zookeeper"]
#   }
#
#   healthcheck {
#     test     = ["CMD", "bash", "-c", "echo ruok | nc localhost 2181"]
#     interval = "10s"
#     timeout  = "5s"
#     retries  = 5
#   }
#
#   cpu_shares = 256
#   memory     = 512 # 512MB
# }
#
# # ==================== Kafka ====================
# resource "docker_image" "kafka" {
#   name         = "confluentinc/cp-kafka:7.4.0"
#   keep_locally = true
# }
#
# resource "docker_container" "kafka" {
#   name       = "kafka"
#   image      = docker_image.kafka.image_id
#   restart    = "always"
#   depends_on = [docker_container.zookeeper]
#
#   env = [
#     "KAFKA_BROKER_ID=1",
#     "KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181",
#     "KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092",
#     "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT",
#     "KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT",
#     "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1",
#     "KAFKA_AUTO_CREATE_TOPICS_ENABLE=true",
#     "KAFKA_NUM_PARTITIONS=3"
#   ]
#
#   ports {
#     internal = 9092
#     external = 9092
#     ip       = "0.0.0.0"
#   }
#
#   networks_advanced {
#     name    = docker_network.app_network.name
#     aliases = ["kafka"]
#   }
#
#   healthcheck {
#     test     = ["CMD", "kafka-topics", "--bootstrap-server", "localhost:9092", "--list"]
#     interval = "15s"
#     timeout  = "10s"
#     retries  = 5
#   }
#
#   cpu_shares = 512
#   memory     = 1024 # 1GB
# }
#
# # ==================== MinIO ====================
# resource "docker_volume" "minio_data" {
#   name = "minio_data"
# }
#
# resource "docker_image" "minio" {
#   name         = "quay.io/minio/minio:latest"
#   keep_locally = true
# }
#
# resource "docker_container" "minio" {
#   name    = "minio"
#   image   = docker_image.minio.image_id
#   restart = "always"
#
#   env = [
#     "MINIO_ROOT_USER=${var.minio_root_user}",
#     "MINIO_ROOT_PASSWORD=${var.minio_root_password}"
#   ]
#
#   command = ["server", "/data", "--console-address", ":9001"]
#
#   ports {
#     internal = 9000
#     external = 9000
#     ip       = "0.0.0.0"
#   }
#
#   ports {
#     internal = 9001
#     external = 9001
#     ip       = "0.0.0.0"
#   }
#
#   volumes {
#     volume_name    = docker_volume.minio_data.name
#     container_path = "/data"
#     read_only      = false
#   }
#
#   networks_advanced {
#     name    = docker_network.app_network.name
#     aliases = ["minio"]
#   }
#
#   healthcheck {
#     test     = ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
#     interval = "5s"
#     timeout  = "5s"
#     retries  = 5
#   }
#
#   cpu_shares = 512
#   memory     = 1024 # 1GB
# }
#
# # ==================== Инициализация MinIO ====================
# resource "docker_image" "mc" {
#   name         = "quay.io/minio/mc:latest"
#   keep_locally = true
# }
#
# # Временный контейнер для инициализации MinIO
# resource "docker_container" "minio_init" {
#   name    = "minio-init"
#   image   = docker_image.mc.image_id
#   restart = "no"
#
#   # Переопределяем entrypoint на /bin/sh
#   entrypoint = ["/bin/sh", "-c"]
#
#   # Команда для выполнения
#   command = [<<-EOT
#     echo "Waiting for MinIO to be ready..."
#
#     # ждать пока mc сможет подключиться к серверу
#     until /usr/bin/mc admin info minio >/dev/null 2>&1; do
#       /usr/bin/mc alias set minio http://minio:9000 ${var.minio_root_user} ${var.minio_root_password} >/dev/null 2>&1 || true
#       sleep 2
#     done
#
#     echo "Setting up MinIO alias..."
#     /usr/bin/mc alias set minio http://minio:9000 ${var.minio_root_user} ${var.minio_root_password}
#
#     echo "Creating bucket '${var.minio_bucket}'..."
#     /usr/bin/mc mb minio/${var.minio_bucket} --ignore-existing
#
#     echo "Setting bucket policy to public..."
#     /usr/bin/mc anonymous set public minio/${var.minio_bucket}
#
#     echo "Listing buckets to verify..."
#     /usr/bin/mc ls minio/
#
#     echo "MinIO initialization complete!"
#     EOT
#   ]
#
#   networks_advanced {
#     name = docker_network.app_network.name
#   }
#
#   # Зависит от основного контейнера MinIO
#   depends_on = [docker_container.minio]
#
#   # Удаляем контейнер после выполнения (очистка)
#   rm = true
# }
#
#
# # ==================== Тестовый продюсер Kafka ====================
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
    name    = docker_network.app_network.name
    aliases = ["nexus"]
  }
  
  healthcheck {
    test     = ["CMD", "curl", "-f", "http://localhost:8081/"]
    interval = "30s"
    timeout  = "10s"
    retries  = 5
  }
  
  # Nexus требует больше памяти
  cpu_shares = 1024
  memory     = 2048  # 2GB минимум для Nexus
  memory_swap = 4096
}
