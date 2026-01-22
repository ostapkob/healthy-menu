pipeline {
    agent { label 'docker' }
    stages {
  
        stage('Checkout') {
            steps {
                git(
                    url: 'http://gitlab:8060/ostapkob/admin-backend',
                    branch: 'master',
                    credentialsId: 'gitlab-token'
                )
            }
        }
  
        stage('Test docker') {
            steps {
                sh '''
                    docker version
                '''
            }
        }
    }
}

