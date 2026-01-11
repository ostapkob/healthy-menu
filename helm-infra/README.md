# Добавить репозиторий в Helm
helm repo add nexus http://nexus.healthy-menu.local/repository/helm-hosted/
helm repo update


# run
helm install order-backend . --set tag=1.0.1

