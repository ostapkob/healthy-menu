# Для локальной разработки
ln -Lf env_example .env
ln -Lf env_example admin-backend/.env
ln -Lf env_example order-backend/.env
ln -Lf env_example courier-backend/.env
ln -Lf env_example migrations/.env
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
bash setup-models.sh
bash load_data.sh

# MiniO
auto created bucket in docker-compose

# GitLab
get password:  $ docker exec gitlab cat /etc/gitlab/initial_root_password 
login: root
- change password
- create token (select api) and add to .env how GITLAB_ROOT_TOKEN
- bash push-to-gitlab.sh (первый раз потребуется ввести логопас)
- add id_rsa.pub in web-interface


# Jenkins
docker-compose up -d --build jenkins
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
install suggest plugins (main thing is to install the Pipeline)
docker cp ./jenkins/*  jenkins:/var/jenkins_home
docker-compose restart jenkins

add node (name agent-1, label - docker),
add secret to .env how JENKINS_SECRET

docker-compose up -d --build jenkins-agent


# Helm
## Добавить репозиторий в Helm
helm repo add nexus http://nexus:8081/repository/helm-hosted/
helm repo update

vim /etc/docker/daemon.json
{
    "insecure-registries" : ["nexus:5000"]
}
sudo systemctl daemon-reload
sudo systemctl restart docker

helm uninstall order-backend
helm install order-backend . --set tag=1.0.1



# TODO

- [ ] Change .env -> values
- [ ] Add Vault | HashiCorp
- [ ] Add Argo
- [ ] Add triger 


