#!/bin/bash
# Синхронизация секретов из Vault в Kubernetes Secret

set -e

NAMESPACE="${1:-healthy-menu-dev}"

echo "🔐 Синхронизация секретов из Vault в Kubernetes ($NAMESPACE)"

# PostgreSQL
echo "📦 PostgreSQL..."
POSTGRES_USER=$(kubectl exec -n vault vault-0 -- vault kv get -field=POSTGRES_USER secret/data/postgres)
POSTGRES_PASSWORD=$(kubectl exec -n vault vault-0 -- vault kv get -field=POSTGRES_PASSWORD secret/data/postgres)
POSTGRES_DB=$(kubectl exec -n vault vault-0 -- vault kv get -field=POSTGRES_DB secret/data/postgres)
POSTGRES_HOST=$(kubectl exec -n vault vault-0 -- vault kv get -field=POSTGRES_HOST secret/data/postgres)
POSTGRES_PORT=$(kubectl exec -n vault vault-0 -- vault kv get -field=POSTGRES_PORT secret/data/postgres)

kubectl create secret generic postgres-secret -n $NAMESPACE \
  --from-literal=POSTGRES_USER="$POSTGRES_USER" \
  --from-literal=POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
  --from-literal=POSTGRES_DB="$POSTGRES_DB" \
  --from-literal=POSTGRES_HOST="$POSTGRES_HOST" \
  --from-literal=POSTGRES_PORT="$POSTGRES_PORT" \
  --dry-run=client -o yaml | kubectl apply -f -

# MinIO
echo "📦 MinIO..."
MINIO_HOST=$(kubectl exec -n vault vault-0 -- vault kv get -field=MINIO_HOST secret/data/minio)
MINIO_PORT=$(kubectl exec -n vault vault-0 -- vault kv get -field=MINIO_PORT secret/data/minio)
MINIO_ROOT_USER=$(kubectl exec -n vault vault-0 -- vault kv get -field=MINIO_ROOT_USER secret/data/minio)
MINIO_ROOT_PASSWORD=$(kubectl exec -n vault vault-0 -- vault kv get -field=MINIO_ROOT_PASSWORD secret/data/minio)
MINIO_BUCKET=$(kubectl exec -n vault vault-0 -- vault kv get -field=MINIO_BUCKET secret/data/minio)

kubectl create secret generic minio-secret -n $NAMESPACE \
  --from-literal=MINIO_HOST="$MINIO_HOST" \
  --from-literal=MINIO_PORT="$MINIO_PORT" \
  --from-literal=MINIO_ROOT_USER="$MINIO_ROOT_USER" \
  --from-literal=MINIO_ROOT_PASSWORD="$MINIO_ROOT_PASSWORD" \
  --from-literal=MINIO_BUCKET="$MINIO_BUCKET" \
  --dry-run=client -o yaml | kubectl apply -f -

# Kafka
echo "📦 Kafka..."
KAFKA_BOOTSTRAP_SERVERS=$(kubectl exec -n vault vault-0 -- vault kv get -field=KAFKA_BOOTSTRAP_SERVERS secret/data/kafka)

kubectl create secret generic kafka-secret -n $NAMESPACE \
  --from-literal=KAFKA_BOOTSTRAP_SERVERS="$KAFKA_BOOTSTRAP_SERVERS" \
  --dry-run=client -o yaml | kubectl apply -f -

# ConfigMap для не-sensitive данных
echo "📦 ConfigMaps..."

kubectl create configmap postgres-config -n $NAMESPACE \
  --from-literal=POSTGRES_HOST="$POSTGRES_HOST" \
  --from-literal=POSTGRES_PORT="$POSTGRES_PORT" \
  --from-literal=POSTGRES_DB="$POSTGRES_DB" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create configmap minio-config -n $NAMESPACE \
  --from-literal=MINIO_HOST="$MINIO_HOST" \
  --from-literal=MINIO_PORT="$MINIO_PORT" \
  --from-literal=MINIO_BUCKET="$MINIO_BUCKET" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create configmap kafka-config -n $NAMESPACE \
  --from-literal=KAFKA_BOOTSTRAP_SERVERS="$KAFKA_BOOTSTRAP_SERVERS" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✅ Синхронизация завершена!"
echo ""
echo "Созданные Secret:"
kubectl get secret -n $NAMESPACE | grep -E "postgres|minio|kafka"
echo ""
echo "Созданные ConfigMap:"
kubectl get configmap -n $NAMESPACE | grep -E "postgres|minio|kafka"
