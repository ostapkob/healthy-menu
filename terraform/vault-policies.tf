# =============================================================================
# HashiCorp Vault Policies & Roles for Kubernetes
# =============================================================================
# Этот файл создаёт:
# - Vault policies (правила доступа к секретам)
# - Vault roles для Kubernetes ServiceAccount
# =============================================================================

# -----------------------------------------------------------------------------
# Policy для External Secrets Operator
# -----------------------------------------------------------------------------
# ESO может читать ВСЕ секреты в secret/dev/*
resource "vault_policy" "external_secrets" {
  name = "external-secrets-policy"

  policy = <<EOT
# Чтение всех секретов в dev окружении
path "secret/data/dev/*" {
  capabilities = ["read", "list"]
}

# Чтение метаданных (для проверки версий)
path "secret/metadata/dev/*" {
  capabilities = ["read", "list"]
}
EOT
}

# -----------------------------------------------------------------------------
# Policy для Admin Backend
# -----------------------------------------------------------------------------
resource "vault_policy" "admin_backend" {
  name = "admin-backend-policy"

  policy = <<EOT
# PostgreSQL
path "secret/data/dev/postgres" {
  capabilities = ["read"]
}

# Kafka
path "secret/data/dev/kafka" {
  capabilities = ["read"]
}

# MinIO
path "secret/data/dev/minio" {
  capabilities = ["read"]
}

# JWT
path "secret/data/dev/jwt" {
  capabilities = ["read"]
}
EOT
}

# -----------------------------------------------------------------------------
# Policy для Order Backend
# -----------------------------------------------------------------------------
resource "vault_policy" "order_backend" {
  name = "order-backend-policy"

  policy = <<EOT
# PostgreSQL
path "secret/data/dev/postgres" {
  capabilities = ["read"]
}

# Kafka
path "secret/data/dev/kafka" {
  capabilities = ["read"]
}

# MinIO
path "secret/data/dev/minio" {
  capabilities = ["read"]
}

# JWT
path "secret/data/dev/jwt" {
  capabilities = ["read"]
}
EOT
}

# -----------------------------------------------------------------------------
# Policy для Courier Backend
# -----------------------------------------------------------------------------
resource "vault_policy" "courier_backend" {
  name = "courier-backend-policy"

  policy = <<EOT
# PostgreSQL
path "secret/data/dev/postgres" {
  capabilities = ["read"]
}

# Kafka
path "secret/data/dev/kafka" {
  capabilities = ["read"]
}

# MinIO
path "secret/data/dev/minio" {
  capabilities = ["read"]
}

# JWT
path "secret/data/dev/jwt" {
  capabilities = ["read"]
}
EOT
}

# -----------------------------------------------------------------------------
# Policy для Jenkins (нужен доступ к Nexus, GitLab, ArgoCD)
# -----------------------------------------------------------------------------
resource "vault_policy" "jenkins" {
  name = "jenkins-policy"

  policy = <<EOT
# Nexus
path "secret/data/dev/nexus" {
  capabilities = ["read"]
}

# GitLab
path "secret/data/dev/gitlab" {
  capabilities = ["read"]
}

# ArgoCD
path "secret/data/dev/argocd" {
  capabilities = ["read"]
}

# SonarQube
path "secret/data/dev/sonarqube" {
  capabilities = ["read"]
}
EOT
}

# =============================================================================
# Vault Roles для Kubernetes Authentication
# =============================================================================
# Roles создаются через скрипт vault-k8s-init.sh
# Эти ресурсы закомментированы чтобы избежать конфликтов
# =============================================================================

# -----------------------------------------------------------------------------
# Role для External Secrets Operator
# -----------------------------------------------------------------------------
# resource "vault_kubernetes_auth_backend_role" "external_secrets" {
#   backend                          = "kubernetes"
#   role_name                        = "external-secrets-role"
#   bound_service_account_names      = ["external-secrets-sa"]
#   bound_service_account_namespaces = ["external-secrets"]
#   token_ttl                        = 3600
#   policies                         = [vault_policy.external_secrets.name]
# }

# -----------------------------------------------------------------------------
# Role для Admin Backend
# -----------------------------------------------------------------------------
# resource "vault_kubernetes_auth_backend_role" "admin_backend" {
#   backend                          = "kubernetes"
#   role_name                        = "admin-backend-role"
#   bound_service_account_names      = ["admin-backend"]
#   bound_service_account_namespaces = ["healthy-menu-dev"]
#   token_ttl                        = 3600
#   policies                         = [vault_policy.admin_backend.name]
# }

# -----------------------------------------------------------------------------
# Role для Order Backend
# -----------------------------------------------------------------------------
# resource "vault_kubernetes_auth_backend_role" "order_backend" {
#   backend                          = "kubernetes"
#   role_name                        = "order-backend-role"
#   bound_service_account_names      = ["order-backend"]
#   bound_service_account_namespaces = ["healthy-menu-dev"]
#   token_ttl                        = 3600
#   policies                         = [vault_policy.order_backend.name]
# }

# -----------------------------------------------------------------------------
# Role для Courier Backend
# -----------------------------------------------------------------------------
# resource "vault_kubernetes_auth_backend_role" "courier_backend" {
#   backend                          = "kubernetes"
#   role_name                        = "courier-backend-role"
#   bound_service_account_names      = ["courier-backend"]
#   bound_service_account_namespaces = ["healthy-menu-dev"]
#   token_ttl                        = 3600
#   policies                         = [vault_policy.courier_backend.name]
# }

# -----------------------------------------------------------------------------
# Role для Jenkins
# -----------------------------------------------------------------------------
# resource "vault_kubernetes_auth_backend_role" "jenkins" {
#   backend                          = "kubernetes"
#   role_name                        = "jenkins-role"
#   bound_service_account_names      = ["jenkins"]
#   bound_service_account_namespaces = ["default"]
#   token_ttl                        = 3600
#   policies                         = [vault_policy.jenkins.name]
# }
