
output "minio_connection" {
  description = "MinIO connection details"
  value = {
    console_url = "http://localhost:9001"
    api_url     = "http://localhost:9000"
    bucket      = var.minio_bucket
  }
  sensitive = false
}

output "kafka_connection" {
  description = "Kafka connection details"
  value = {
    bootstrap_server = "localhost:9092"
    zookeeper        = "localhost:2181"
  }
  sensitive = false
}

output "gitlab_connection" {
  description = "GitLab connection details"
  value = {
    web_url = "${var.gitlab_external_url}:${var.gitlab_http_port}"
    ssh_url = "ssh://git@127.0.0.1:${var.gitlab_ssh_port}"
  }
  sensitive = false
}

output "nexus_connection" {
  description = "Nexus connection details"
  value = {
    web_url      = "http://localhost:${var.nexus_host_port}"
    registry_url = "localhost:${var.nexus_registry_port}"
  }
  sensitive = false
}

output "docker_network" {
  description = "Docker network details"
  value = {
    name   = "app-network"
    subnet = "172.21.0.0/24" # Изменён подсеть для избежания конфликтов
  }
  sensitive = false
}


output "sonarqube_connection" {
  description = "SonarQube connection details"
  value = {
    web_url          = "http://localhost:${var.sonar_web_port}"
    default_login    = "admin"
    default_password = "admin"
    db_connection = {
      host     = "postgres-sonar"
      port     = 5432
      database = var.sonar_postgres_db
      user     = var.sonar_postgres_user
    }
    api_status   = "http://localhost:${var.sonar_web_port}/api/system/status"
    logs_command = "docker logs -f sonarqube"
  }
  sensitive = true
}



locals {
  env_path = "${path.module}/../.env"
  env_text = file(local.env_path)
  matched_lines = [
    for l in split("\n", local.env_text) : trimspace(l) # Используем trimspace вместо trim
    if trimspace(l) != "" && (
      can(regex("^GITLAB_ROOT_TOKEN", l)) ||
      can(regex("^GITLAB_ACCESS_TOKEN", l)) ||
      can(regex("^SONAR_USER_TOKEN", l)) ||
      can(regex("^SONAR_ADMIN_TOKEN", l))
    )
  ]
  matched_map = {
    for pair in local.matched_lines :
    split("=", pair)[0] => (length(split("=", pair)) > 1 ? join("=", slice(split("=", pair), 1, length(split("=", pair)))) : "")
  }
}

output "env_matched_lines" {
  value      = local.matched_lines
  depends_on = [terraform_data.bootstrap] # outputs ignore depends_on at plan, but keeps intent
}

output "env_matched_map" {
  value     = local.matched_map
  sensitive = true
}

# output "generated_files" {
#   description = "Generated configuration files"
#   value = {
#     env_file = local_file.env_file.filename
#     examples = [for k, v in local_file.example_configs : v.filename]
#   }
#   sensitive = false
# }
