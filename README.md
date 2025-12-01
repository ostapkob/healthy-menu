bash build-services.sh
uvicorn admin.main:app --reload --port 8002

source venv/bin/activate
alembic revision --autogenerate -m "create all tables"
alembic upgrade head
bash load_data.sh

kafka-topics --bootstrap-server localhost:9092 --list
kafka-console-producer --bootstrap-server localhost:9092 --topic new_orders
{"order_id": 123, "user_id": 458}
kafka-console-consumer --bootstrap-server localhost:9092 --topic new_orders --from-beginning
echo "127.0.0.1       kafka" >>  /etc/hosts
kcat -b kafka:9092 -t new_orders -C


INSERT INTO couriers (id, name, status, current_order_id) VALUES (1, 'Курьер 1', 'available', NULL);
UPDATE couriers SET status = 'available' WHERE id = 1;
