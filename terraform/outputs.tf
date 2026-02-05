output "postgres_connection" {
  description = "PostgreSQL connection details"
  value = {
    host     = "localhost"
    port     = 5432
    database = var.postgres_db
    user     = var.postgres_user
  }
  sensitive = true
}

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
    web_url       = "${var.gitlab_external_url}:${var.gitlab_http_port}"
    ssh_url       = "ssh://git@127.0.0.1:${var.gitlab_ssh_port}"
    initial_password = "docker exec gitlab cat /etc/gitlab/initial_root_password"
    logs          = "docker logs -f gitlab"
    status        = "docker exec gitlab gitlab-ctl status"
  }
  sensitive = false
}

output "nexus_connection" {
  description = "Nexus connection details"
  value = {
    web_url            = "http://localhost:${var.nexus_host_port}"
    registry_url       = "localhost:${var.nexus_registry_port}"
    initial_password   = "docker exec nexus cat /nexus-data/admin.password"
    logs               = "docker logs -f nexus"
  }
  sensitive = false
}

output "docker_network" {
  description = "Docker network details"
  value = {
    name    = docker_network.app_network.name
    subnet  = "172.21.0.0/24"
  }
  sensitive = false
}


# output "generated_files" {
#   description = "Generated configuration files"
#   value = {
#     env_file = local_file.env_file.filename
#     examples = [for k, v in local_file.example_configs : v.filename]
#   }
#   sensitive = false
# }
