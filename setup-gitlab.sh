# !/bin/bash
 
set -o allexport
source ./.env
set +o allexport

pink='\033[1;35m'
reset='\033[0m'

echo "Create user..."

response=$(curl --header "PRIVATE-TOKEN: $GITLAB_ROOT_TOKEN" \
     --data "username=$GITLAB_USER" \
     --data "name=$GITLAB_NAME" \
     --data "email=$GITLAB_EMAIL" \
     --data "password=$GITLAB_PASSWORD" \
     --request POST "$GITLAB_URL/api/v4/users"
     )

user_id=$(echo $response | jq -r '.id')

echo 'Create token'

response=$(curl --header "PRIVATE-TOKEN: $GITLAB_ROOT_TOKEN" \
     --data "name=$GITLAB_NAME" \
     --data "scopes[]=api" \
     --data "expires_at=2026-03-31" \
     --request POST "$GITLAB_URL/api/v4/users/$user_id/personal_access_tokens"
     )

token=$(echo $response | jq -r '.token')



echo -e "\n‼️Save user $GITLAB_NAME in .env how GITLAB_TOKEN"
echo -e "${pink}${token}${reset}"
echo -e "\nDone!"
