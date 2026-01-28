# Установите Minikube если нужно
minikube start

# Включите ingress
minikube addons enable ingress

# Соберите образ
eval $(minikube docker-env)
docker build -t healthy-menu-admin:latest -f backend/admin/Dockerfile ./backend

## Registry Локально (для Minikube)
eval $(minikube docker-env) в моем случае не работает

## поэтому
minikube start --insecure-registry my-private-registry:5000
echo "$(minikube ip) my-private-registry" | sudo tee -a /etc/hosts
minikube ssh -- docker run -d -p 5000:5000 --restart=always --name registry registry:2


# Получить IP Minikube
MINIKUBE_IP=$(minikube ip)

# Тегировать образ
docker tag ваш-образ:latest ${MINIKUBE_IP}:5000/ваш-образ:latest

# Или используя имя хоста
docker tag ваш-образ:latest my-private-registry:5000/ваш-образ:latest

# Загрузить в registry
docker push ${MINIKUBE_IP}:5000/ваш-образ:latest

# Проверка
minikube ssh -- "curl http://localhost:5000/v2/_catalog"

# в деплое
image: localhost:5000/admin-backend:latest

# Если registry работает
./publish-to-registry.sh


# Примените манифесты
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/configmap.yaml

# Test minio
echo 'host.minikube.internal' > /etc/hosts
kubectl run -it --rm test --image=alpine -- sh
apk add --no-cache curl
curl -v http://host.minikube.internal:9000/healthy-menu-dishes/

# Nexus
./setup-nexus.sh
./publish-to-registry.sh


# Minikube
minikube delete

minikube start \
  --insecure-registry="nexus:5000" \
  --insecure-registry="nix:5000" \
  --insecure-registry="192.168.49.0/24"  # Весь диапазон IP minikube

minikube ssh "echo '192.168.1.163 nexus jenkins gitlab' | sudo tee -a /etc/hosts"
minikube ssh "echo '192.168.1.171 minio kafka postgres' | sudo tee -a /etc/hosts"
minikube ssh "curl http://nexus:5000/v2/_catalog"


# Для публиации в nexus
 в /etc/docker/daemon.json
{
  "insecure-registries": ["$(minikube ip):5000", "127.0.0.1:5000"]
}
sudo systemctl restart docker
