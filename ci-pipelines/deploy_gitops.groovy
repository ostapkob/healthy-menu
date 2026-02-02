pipeline {
  agent { label 'docker' }
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
            script: "curl -s 'http://nexus:5000/v2/${SERVICE}/tags/list' | jq -r '.tags[]'",
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
          // Получаем URL с credentials
          def repoUrl = 'http://gitlab:8060/ostapkob/healthy-menu-gitops.git'
      
          // Альтернатива: использовать SSH URL если доступен
          // def repoUrl = 'git@gitlab:8060:ostapkob/healthy-menu-gitops.git'
      
          withCredentials([usernamePassword(
            credentialsId: 'gitlab-token',
            usernameVariable: 'GIT_USERNAME',
            passwordVariable: 'GIT_PASSWORD'
          )]) {
            // Клонируем с авторизацией в URL
            sh """
              git clone http://${GIT_USERNAME}:${GIT_PASSWORD}@gitlab:8060/ostapkob/healthy-menu-gitops.git
              cd healthy-menu-gitops
              git config user.email "jenkins@ci"
              git config user.name "Jenkins"
          
              sed -i 's/tag:.*/tag: "${TAG}"/' values-${SERVICE}.yaml
          
              if git diff --quiet; then
                echo "No changes"
              else
                git add .
                git commit -m "Deploy ${SERVICE}:${TAG}"
                git push origin master
              fi
            """
          }
        }
      }
    }

  }
}
