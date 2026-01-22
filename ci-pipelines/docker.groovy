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
        stage('Build test image') {
            steps {
                sh '''
                    docker build -f Dockerfile.test -t admin-backend:test .;
                '''
            }
        }
        stage('Tests') {
            steps {
                sh '''
                    docker run --rm admin-backend:test;
                '''
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}

