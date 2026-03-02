.PHONY: tmux load-data publish push-gitlab setup-gitlab setup-models setup-nexus setup-sonar jenkins-backup vault-init create-image-pull-secret

tmux:
	bash scripts/tmux.sh

jenkins-backup:
	bash scripts/cleanup_jenkins_backup.sh jenkins/jenkins_home

load-data:
	bash scripts/load-data.sh

publish:
	bash scripts/publish-to-registry.sh

push-gitlab:
	bash scripts/push-to-gitlab.sh

setup-gitlab:
	bash scripts/setup-gitlab.sh

setup-models:
	bash scripts/setup-models.sh

setup-nexus:
	bash scripts/setup-nexus.sh

setup-sonar:
	bash scripts/setup-sonar.sh

vault-init:
	bash scripts/vault-init.sh

# Создание imagePullSecret для доступа к Nexus registry
create-image-pull-secret:
	@source .env && \
	kubectl create secret docker-registry nexus-creds \
		--docker-server=$${NEXUS_REGISTRY_URL:-nexus:5000} \
		--docker-username=$${NEXUS_USER_NAME} \
		--docker-password=$${NEXUS_USER_PASSWORD} \
		--docker-email=noreply@example.com \
		-n healthy-menu-dev \
		--dry-run=client -o yaml | kubectl apply -f -
