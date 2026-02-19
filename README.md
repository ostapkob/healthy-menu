# Для локальной разработки ln -Lf env_example .env ln -Lf env_example admin-backend/.env
ln -f env_example admin-backend/.env
ln -f env_example order-backend/.env
ln -f env_example courier-backend/.env
ln -f env_example migrations/.env
ln -f env_example terraform/.env
ln -f env_example .env
export $(grep -v '^#' .env | xargs)

echo "127.0.0.1       kafka postgres minio" >>  /etc/hosts
у меня на другом сервере тогда так
192.168.1.163 jenkins gitlab nexus

# python
cd admin-backend
uv run uvicorn main:app  --port 8002
PYTHONPATH=. uv run pytest tests -v

# docker
docker build -t admin-backend .
## Del all
docker rmi -f $(docker images -aq)
docker volume prune
docker rm -vf $(docker ps -aq)

# docker-compose
docker-compose up -d --build
docker-compose --profile infra up -d --build
docker-compose --profile infra down

# Kafka
kafka-topics --bootstrap-server localhost:9092 --list
kafka-console-producer --bootstrap-server localhost:9092 --topic new_orders
{"order_id": 123, "user_id": 458}
kafka-console-consumer --bootstrap-server localhost:9092 --topic new_orders --from-beginning
kcat -b kafka:9092 -t new_orders -C

# SQL
install csvkit
make setup-models
make load_data
CREATE DATABASE food_db_tests WITH TEMPLATE food_db;

# MiniO
auto created bucket in docker-compose

# GitLab
- make setup-gitlab
- make push-to-gitlab (первый раз потребуется ввести логопас)
how root:
- Admin → Settings → Network → Outbound requests
- ✅ Allow requests to the local network from webhooks and integrations
- в whitelist добавить http://jenkins:8080 или IP/домен ($ docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' gitlab )

# Jenkins
docker-compose up -d --build jenkins
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
install suggest plugins (main thing is to install the Pipeline)
docker cp ./jenkins/jenkins_home  jenkins:/var/
docker-compose restart jenkins

add node (name agent-1, label - docker),
add secret to .env how JENKINS_SECRET

docker-compose up -d --build jenkins-agent
add cred gitlab-token: username=ostapkob, token=GITLAB_ACCESS_TOKEN

test WebHook:
```
curl -v \
-X POST \
-H "Content-Type: application/json" \
-H "X-Gitlab-Event: Merge Request Hook" \
-d '{
  "object_kind": "merge_request",
  "event_type": "merge_request",
  "project": {
    "path_with_namespace": "ostapkob/admin-backend"
  },
  "object_attributes": {
    "action": "merged",
    "source_branch": "feature/some-feature",
    "target_branch": "master"
  }
}' \
"http://jenkins:8080/generic-webhook-trigger/invoke?token=gitlab-mr-build"
```


# SonarQube
admin
admin

Создать токен и добавить его в Jenkins
My Account -> Security -> Global

Administration -> Configuration -> Webhooks
URL: http://jenkins:8080/sonarqube-webhook/


# Argo
minikube start --insecure-registry="nexus:5000" --insecure-registry="192.168.1.193/24"
kubectl create namespace argocd
kubectl create namespace healthy-menu-dev
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
### Скачиваем свежий манифест CRDs (stable ветка на февраль 2026)
curl -LO https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/crds/applicationset-crd.yaml
kubectl apply --server-side --force-conflicts -f applicationset-crd.yaml
rm  applicationset-crd.yaml
kubectl get crd | grep argoproj.io

kubectl port-forward --address localhost,192.168.1.163 svc/argocd-server -n argocd 18080:443

argocd admin initial-password -n argocd

argocd login localhost:18080 --username admin --password $ARGO_PASSWORD --insecure
argocd logout localhost:18080

docker network connect app-network minikube
docker network disconnect -f app-network minikube

argocd repo add http://gitlab:80/ostapkob/infra.git \
  --username git \
  --password $GITLAB_ACCESS_TOKEN \
  --name infra

argocd repo add http://gitlab:80/ostapkob/gitops.git \
  --username git \
  --password $GITLAB_ACCESS_TOKEN \
  --name gitops

kubectl apply -f argocd-appsets/dev-appset.yaml -n argocd
kubectl delete appset healthy-menu-dev -n argocd


# Terraform

terraform apply -target=docker_container.jenkins_agent
```
# Очищаем данные Nexus (если нужно переконфигурировать)

terraform state rm null_resource.nexus_init

docker stop nexus
docker rm nexus
docker volume rm nexus_data

# Применяем заново
terraform apply -auto-approve
```

# Nexus
make setup-nexus

kubectl create secret docker-registry nexus-creds \
  --docker-server=nexus:5000 \
  --docker-username=ostapkob \
  --docker-password=superpass123 \
  --docker-email=any@example.com -o yaml > nexus-secret.yaml

# Istio
curl -L https://istio.io/downloadIstio | sh -
istioctl install --set profile=default --skip-confirmation

kubectl label namespace healthy-menu-dev istio-injection=enabled --overwrite
kubectl label namespace healthy-menu-dev istio-injection-

kubectl rollout restart deployment -n healthy-menu-dev

kubectl apply -f gateway.yaml
kubectl apply -f virtualservice.yaml



# TODO
- [x] Add webhook
- [x] SonarQube
- [x] Argo
- [x] Change .env -> values
- [x] Terraform
- [X] Docker in Docker
- [x] rename healthy-menu-
- [ ] Vault HashiCorp
- [ ] Istio
- [ ] Fluenbit
- [ ] Prometheus
- [ ] Grafana
- [ ] https

