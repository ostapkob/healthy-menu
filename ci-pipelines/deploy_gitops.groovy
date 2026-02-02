pipeline {
  agent { label 'docker' }
  environment {
      NEXUS_REGISTRY_URL = "${NEXUS_REGISTRY_URL}"
  }
  stages {
    stage('Select Service') {
      steps {
        script {
          SERVICE = input message: 'Choose service', parameters: [
            choice(
              choices: [
                '',
                'admin-backend',
                'admin-frontend',
                'courier-backend', 
                'courier-frontend',
                'order-backend',
                'order-frontend'
              ],
              name: 'SERVICE'
            )
          ]
        }
      }
    }
    stage('Nexus Tags') {
      steps {
        script {
          // Получаем теги и преобразуем в список
          def tagsOutput = sh(
            script: "curl -s '${NEXUS_REGISTRY_URL}/${SERVICE}/tags/list' | jq -r '.tags[]'",
            returnStdout: true
          ).trim()
          
          // Разбиваем по строкам и фильтруем пустые значения
          def TAGS = tagsOutput.split('\n').findAll { it.trim() }
          
          // Если тегов нет, добавляем пустую строку
          if (TAGS.isEmpty()) {
            TAGS = ['']
          }
          
          TAG = input message: 'Choose tag', parameters: [
            choice(choices: TAGS, name: 'TAG')
          ]
        }
      }
    }
    stage('Update GitOps') {
      steps {
        script {
          // Работаем во временной директории
          def workspaceDir = pwd()
          def repoDir = "${workspaceDir}/gitops-repo-${BUILD_NUMBER}"
          
          try {
            // Клонируем репозиторий
            withCredentials([usernamePassword(
              credentialsId: 'gitlab-token',
              usernameVariable: 'GIT_USER',
              passwordVariable: 'GIT_PASS'
            )]) {
              // Используем переменные окружения для безопасной передачи credentials
              sh """
                GIT_URL="http://${GIT_USER}:${GIT_PASS}@gitlab:8060/ostapkob/healthy-menu-gitops.git"
                git clone "\${GIT_URL}" "${repoDir}"
              """
            }
            
            dir(repoDir) {
              // Настраиваем git
              sh """
                git config user.email "jenkins@${env.NODE_NAME}"
                git config user.name "Jenkins CI"
              """
              
              // Изменяем нужный файл
              sh """
                if [ -f "values-${SERVICE}.yaml" ]; then
                  sed -i 's|tag:.*|tag: "${TAG}"|' "values-${SERVICE}.yaml"
                else
                  echo "ERROR: File values-${SERVICE}.yaml not found!"
                  exit 1
                fi
              """
              
              // Коммитим и пушим
              sh '''
                if git diff --quiet; then
                  echo "No changes to commit"
                else
                  git add .
                  git commit -m "Deploy service with new tag"
                  git push origin master
                fi
              '''
            }
          } finally {
            // Очищаем временную директорию
            sh "rm -rf ${repoDir} 2>/dev/null || true"
          }
        }
      }
    }
  }
  post {
    always {
        cleanWs()
    }
  }
}
