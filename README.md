ln -L env_example .env
ln -L env_example admin-backend/.env
ln -L env_example order-backend/.env
ln -L env_example courier-backend/.env
ln -L env_example migrations/.env

# Для локальной разработки
echo "127.0.0.1       kafka postgres minio nexus" >>  /etc/hosts
у меня на другом сервере тогда так  
192.168.1.163 jenkins gitlab


# python
cd admin-backend
uv run uvicorn main:app  --port 8002
PYTHONPATH=. uv run pytest

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


