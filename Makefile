.PHONY: load-data publish push-gitlab setup-gitlab setup-models setup-nexus setup-sonar tmux jenkins-backup

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

tmux:
	bash scripts/tmux.sh
