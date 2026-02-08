# Для локальной разработки ln -Lf env_example .env ln -Lf env_example admin-backend/.env
ln -Lf env_example admin-backend/.env
ln -Lf env_example order-backend/.env
ln -Lf env_example courier-backend/.env
ln -Lf env_example migrations/.env
ln -Lf env_example .env
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
Создать токен и добавить его в Jenkins 


# Argo
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl port-forward svc/argocd-server -n argocd 8080:443


kubectl apply -f dev/admin-backend/app-admin-backend.yaml -n argocd

argocd repo add http://gitlab:8060/ostapkob/healthy-menu-infra.git \
  --username git \
  --password $GITLAB_ACCESS_TOKEN \
  --name healthy-menu-infra

argocd repo add http://gitlab:8060/ostapkob/healthy-menu-gitops.git \
  --username git \
  --password $GITLAB_ACCESS_TOKEN \
  --name healthy-menu-gitops

# Terraform
```
# Очищаем данные Nexus (если нужно переконфигурировать)

terraform state rm null_resource.nexus_init

docker stop nexus
docker rm nexus
docker volume rm nexus_data

# Применяем заново
terraform apply -auto-approve
```



# TODO
- [x] Add webhook 
- [x] SonarQube
- [x] Argo
- [ ] Terraform
- [ ] Vault HashiCorp
- [ ] Istio
- [ ] Fluenbit
- [ ] Prometheus
- [ ] Grafana
- [ ] Docker in Docker
- [ ] Change .env -> values
- [ ] rename healthy-menu- 

