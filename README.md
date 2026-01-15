# python
cd admin-backend
uv run uvicorn main:app

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
или через переменную окружения:
export COMPOSE_PROFILES=back_front

# Kafka
kafka-topics --bootstrap-server localhost:9092 --list
kafka-console-producer --bootstrap-server localhost:9092 --topic new_orders
{"order_id": 123, "user_id": 458}
kafka-console-consumer --bootstrap-server localhost:9092 --topic new_orders --from-beginning
echo "127.0.0.1       kafka" >>  /etc/hosts
kcat -b kafka:9092 -t new_orders -C

# SQL
alembic init migrations
alembic revision --autogenerate -m "create all tables"
alembic upgrade head
bash load_data.sh
INSERT INTO couriers (id, name, status, current_order_id) VALUES (1, 'Курьер 1', 'available', NULL);
UPDATE couriers SET status = 'available' WHERE id = 1;

# MiniO
./mc alias set minio http://s3.healthy.local minioadmin minioadmin
./mc anonymous set public minio/healthy-menu-dishes

# GitLab

login: root
docker exec gitlab cat /etc/gitlab/initial_root_password
- api
- write_repository
- read_repository
- write_virtual_registry
- manage_runner
