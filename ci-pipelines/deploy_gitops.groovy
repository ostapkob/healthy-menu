pipeline {
  agent { label 'docker' }
  environment {
    GIT_URL = 'gitlab:80/ostapkob/'
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
          // def tagsOutput = sh(
          //   script: "curl -s 'http://nexus:5000/v2/${SERVICE}/tags/list' | jq -r '.tags[]'",
          //   returnStdout: true
          // ).trim()
          def tagsOutput

          withCredentials([usernamePassword(credentialsId: 'nexus-cred',
                                  passwordVariable: 'NEXUS_PWD',
                                  usernameVariable: 'NEXUS_USR')]) {
            tagsOutput = sh(
                script: "curl -s -u \$NEXUS_USR:\$NEXUS_PWD 'http://nexus:5000/v2/${SERVICE}/tags/list' | jq -r '.tags[]'",
                returnStdout: true
              ).trim()
          }

          // Разбиваем по строкам и фильтруем пустые значения
          def TAGS = tagsOutput.split('\n').findAll { it.trim() }.sort().reverse()


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
                GIT_FULL_URL="http://${GIT_USER}:${GIT_PASS}@${GIT_URL}/gitops.git"
                git clone "\${GIT_FULL_URL}" "${repoDir}"
              """
            }

            dir(repoDir) {
              // Настраиваем git
              sh """
                git config user.email "jenkins@${env.NODE_NAME}"
                git config user.name "Jenkins CI"
              """

              // Изменяем нужный файл

              println(">>> ${SERVICE}>>> ${TAG} ")
              sh """
                sed -i 's|tag: .*|tag: \"${TAG}\"|' "services/${SERVICE}.yaml"
                git add "services/${SERVICE}.yaml"
                git commit -m "Deploy ${SERVICE}:${TAG}"
                git push origin master
              """
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
