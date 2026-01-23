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
                    export DOCKER_BUILDKIT=1;
                    docker build -f Dockerfile.test -t admin-backend:test .;
                '''
            }
        }
        stage('Tests') {
            steps {
                sh '''
                    env | grep POSTGRES > /tmp/envfile;
                    env | grep MINIO >> /tmp/envfile;
                    docker run --rm \
                      --env-file /tmp/envfile \
                      --add-host minio:192.168.1.100 \
                      --add-host postgres:192.168.1.100 \
                      admin-backend:test
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

