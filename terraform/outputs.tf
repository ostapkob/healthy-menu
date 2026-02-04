output "postgres_connection" {
  description = "PostgreSQL connection details"
  value = {
    host     = "localhost"
    port     = 5432
    database = var.postgres_db
    user     = var.postgres_user
    password = var.postgres_password
  }
  sensitive = true
}

output "minio_connection" {
  description = "MinIO connection details"
  value = {
    console_url = "http://localhost:9001"
    api_url     = "http://localhost:9000"
    bucket      = var.minio_bucket
    user        = var.minio_root_user
  }
  sensitive = true
}

output "nexus_connection" {
  description = "Nexus connection details"
  value = {
    web_url         = "http://localhost:${var.nexus_host_port}"
    registry_url    = "localhost:${var.nexus_registry_port}"
    admin_user      = "admin"
    admin_password  = var.nexus_admin_password
    user_name       = var.nexus_user_name
    user_password   = var.nexus_user_password
  }
  sensitive = true
}

output "kafka_connection" {
  description = "Kafka connection details"
  value = {
    bootstrap_server = "localhost:9092"
    zookeeper        = "localhost:2181"
    topics           = var.kafka_topics
  }
  sensitive = false
}

output "nexus_status" {
  description = "Nexus initialization status"
  value = {
    container_running = docker_container.nexus.id != null
    init_triggered    = null_resource.nexus_init.id != null
    admin_password    = fileexists("/tmp/nexus_terraform_status.txt") ? "configured" : "pending"
    web_url           = "http://localhost:${var.nexus_host_port}"
    check_command     = "docker exec nexus cat /nexus-data/admin.password 2>/dev/null || echo 'Already configured'"
  }
  sensitive = false
}

output "nexus_credentials" {
  description = "Nexus credentials (use with caution)"
  value = {
    admin_user     = "admin"
    admin_password = var.nexus_admin_password
    user_name      = var.nexus_user_name
    user_password  = var.nexus_user_password
  }
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
