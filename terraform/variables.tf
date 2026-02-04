 # == postgres ==
variable "postgres_user" {
  description = "PostgreSQL username"
  type        = string
  sensitive   = true
}

variable "postgres_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "postgres_db" {
  description = "PostgreSQL database name"
  type        = string
  default     = "food_db"
}

 # == minio ==
variable "minio_root_user" {
  description = "MinIO root username"
  type        = string
  sensitive   = true
}

variable "minio_root_password" {
  description = "MinIO root password"
  type        = string
  sensitive   = true
}

variable "minio_bucket" {
  description = "MinIO bucket name"
  type        = string
  default     = "healthy-menu-dishes"
}


 # == kafka ==
variable "kafka_topics" {
  description = "List of Kafka topics to create"
  type        = list(string)
  default     = ["orders", "events", "notifications"]
}

# == nexus ==
variable "nexus_host_port" {
  type    = number
  default = 8081
}

variable "nexus_registry_port" {
  type    = number
  default = 5000
}

variable "nexus_admin_password" {
  type      = string
  sensitive = true
}

variable "nexus_user_name" {
  type = string
}

variable "nexus_user_password" {
  type      = string
  sensitive = true
}










# variable "jenkins_plugins" {
#   description = "List of Jenkins plugins to pre-install"
#   type        = list(string)
#   default = [
#     "git",
#     "docker-plugin",
#     "docker-workflow",
#     "pipeline",
#     "blueocean",
#     "dark-theme",
#     "sonar",
#     "rebuild"
#   ]
# }
