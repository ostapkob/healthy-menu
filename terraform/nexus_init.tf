# ==================== Nexus Initialization ====================
resource "null_resource" "nexus_init" {
  depends_on = [
    docker_container.nexus,
  ]

  triggers = {
    # Запускать при изменении любого из этих параметров
    admin_password   = var.nexus_admin_password
    user_name        = var.nexus_user_name
    user_password    = var.nexus_user_password
    script_content   = filemd5("${path.module}/scripts/nexus_init.sh")
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command = <<-EOT
      echo "🚀 Starting Nexus configuration via external script..."
      echo "   Script: ${path.module}/scripts/nexus_init.sh"
      echo "   Port: ${var.nexus_host_port}"
      echo "   Admin pass: [set]"
      echo "   User: ${var.nexus_user_name}"
      
      # Даём права на выполнение
      chmod +x "${path.module}/scripts/nexus_init.sh"
      
      # Запускаем скрипт
      "${path.module}/scripts/nexus_init.sh" \
        "${var.nexus_host_port}" \
        "${var.nexus_admin_password}" \
        "${var.nexus_user_name}" \
        "${var.nexus_user_password}"
      
      echo "✅ Script execution completed"
    EOT
  }
}

# ==================== Nexus Verification ====================
resource "null_resource" "nexus_verify" {
  depends_on = [null_resource.nexus_init]
  
  triggers = {
    always_run = timestamp()
  }
  
  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command = <<-EOT
      echo "🔍 Verifying Nexus configuration..."
      
      # Ждём немного
      sleep 5
      
      # Проверяем файл статуса
      if [ -f /tmp/nexus_configured.txt ]; then
        echo "📋 Configuration status:"
        cat /tmp/nexus_configured.txt
      else
        echo "⚠️  No configuration status file found"
      fi
      
      # Проверяем пароль
      echo ""
      echo "🔐 Testing credentials..."
      
      if docker exec nexus test -f /nexus-data/admin.password; then
        INITIAL_PASS=$(docker exec nexus cat /nexus-data/admin.password)
        echo "⚠️  Initial password still exists: $$INITIAL_PASS"
      else
        echo "✅ Initial password file removed"
      fi
      
      # Пробуем аутентифицироваться
      echo ""
      echo "🌐 Testing API access..."
      
      if curl -s -u "admin:${var.nexus_admin_password}" \
          "http://localhost:${var.nexus_host_port}/service/rest/v1/status" > /dev/null; then
        echo "✅ API authentication successful with new password"
      else
        echo "❌ API authentication failed"
      fi
    EOT
  }
}
