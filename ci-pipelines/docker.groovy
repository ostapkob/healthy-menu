pipeline {
    agent { label 'docker' }

    parameters {
        choice(
            name: 'SERVICE_NAME',
            choices: [
                'admin-backend',
                'courier-backend', 
                'order-backend',
                'admin-frontend',
                'courier-frontend',
                'order-frontend'
            ],
            description: 'Выберите сервис для сборки'
        )
    }

    environment {
        SERVICE_NAME      = "${params.SERVICE_NAME ?: 'admin-backend'}"
        NEXUS_REGISTRY_URL = "${NEXUS_REGISTRY_URL}"  
        TEST_IMAGE        = "${SERVICE_NAME}:test"
        RELEASE_IMAGE     = "${NEXUS_REGISTRY_URL}/${SERVICE_NAME}:${BUILD_NUMBER}"
        DOCKER_BUILDKIT   = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    // Динамический URL на основе SERVICE_NAME
                    def repoUrl = "http://gitlab:8060/ostapkob/${SERVICE_NAME}"
                    git(
                        url: repoUrl,
                        branch: 'master',
                        credentialsId: 'gitlab-token'
                    )
                }
            }
        }

        stage('Test docker') {
            steps {
                sh 'docker version'
            }
        }

        stage('Build & Test') {
            parallel {
                stage('Build test image') {
                    steps {
                        sh "docker buildx build -f Dockerfile.test -t ${TEST_IMAGE} ."
                    }
                }
            }
        }

        stage('Run tests') {
            steps {
                sh '''
                    env | grep -E "(POSTGRES|MINIO)" > /tmp/envfile
                    docker run --rm \
                      --env-file /tmp/envfile \
                      --add-host minio:${FEDORA} \
                      --add-host postgres:${FEDORA} \
                      --add-host kafka:${FEDORA} \
                      ${TEST_IMAGE}
                '''
            }
        }

        stage('Build release image') {
            steps {
                sh "docker buildx build -f Dockerfile -t ${RELEASE_IMAGE} ."
            }
        }

        stage('Push to Nexus') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'nexus-docker-creds',
                    usernameVariable: 'NEXUS_USER',
                    passwordVariable: 'NEXUS_PASS'
                )]) {
                    sh '''
                        echo "$NEXUS_PASS" | docker login ${NEXUS_REGISTRY_URL} \
                          -u "$NEXUS_USER" --password-stdin

                        docker push ${RELEASE_IMAGE}

                        docker logout ${NEXUS_REGISTRY_URL}
                    '''
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

