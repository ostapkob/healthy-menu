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


# == gitlab ==
variable "gitlab_external_url" {
  description = "External URL for GitLab"
  type        = string
  default     = "http://127.0.0.1"
}

variable "gitlab_http_port" {
  description = "GitLab HTTP port"
  type        = number
  default     = 8060
}

variable "gitlab_ssh_port" {
  description = "GitLab SSH port"
  type        = number
  default     = 2222
}

variable "gitlab_shm_size" {
  description = "GitLab shared memory size"
  type        = number
  default     = 1024 * 1024 * 256 # 256MB в байтах
}

variable "gitlab_memory_limit" {
  description = "GitLab container memory limit (MB)"
  type        = number
  default     = 4096 # 4GB
}

variable "gitlab_root_password" {
  description = "GitLab root password"
  type        = string
  sensitive   = true
}

variable "gitlab_user_name" {
  description = "GitLab username for the new user"
  type        = string
}

variable "gitlab_user_password" {
  description = "GitLab user password (for the new user)"
  type        = string
  sensitive   = true
}

variable "gitlab_root_email" {
  description = "GitLab root email"
  type        = string
  default     = "admin@example.com"
}

variable "gitlab_name" {
  description = "GitLab user's full name"
  type        = string
  default     = "Ostap Kob"
}

variable "gitlab_email" {
  description = "GitLab user email"
  type        = string
  default     = "ostapkob@gmail.com"
}


# == Jenkins ==
variable "jenkins_secret" {
  type        = string
  description = "Jenkins agent secret"
  sensitive   = true
}

variable "jenkins_agent_name" {
  type    = string
  default = "agent-1"
}

variable "jenkins_agent_workdir" {
  type    = string
  default = "/home/jenkins/"
}


# == SonarQube ==
variable "sonar_postgres_user" {
  description = "PostgreSQL user for SonarQube"
  type        = string
  sensitive   = true
}

variable "sonar_postgres_password" {
  description = "PostgreSQL password for SonarQube"
  type        = string
  sensitive   = true
}

variable "sonar_postgres_db" {
  description = "PostgreSQL database name for SonarQube"
  type        = string
  default     = "sonar"
}

variable "sonar_web_port" {
  description = "SonarQube web interface port"
  type        = number
  default     = 9090
}

variable "sonar_es_disable_bootstrap_checks" {
  description = "Disable Elasticsearch bootstrap checks"
  type        = string
  default     = "true"
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
