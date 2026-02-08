pipeline {
    agent { label 'docker' }

    triggers {
        GenericTrigger(
            genericVariables: [
                [key: 'webhookObjectKind', value: '$.object_kind'],
                [key: 'webhookMrState',    value: '$.object_attributes.state'],
                [key: 'webhookRepoName',   value: '$.repository.name'],
                [key: 'webhookProjectNs',  value: '$.project.path_with_namespace']
            ],
            causeString: 'GitLab MR ($webhookMrState) for $webhookProjectNs',
            token: 'gitlab-mr-build',
            printContributedVariables: true,
            printPostContent: true,
            regexpFilterText: '$webhookObjectKind:$webhookMrState',
            regexpFilterExpression: 'merge_request:merged'
        )
    }

    parameters {
        choice(
            name: 'PARAM_SERVICE',
            choices: [
                '',
                'admin-backend',
                'admin-frontend',
                'courier-backend', 
                'courier-frontend',
                'order-backend',
                'order-frontend'
            ],
            description: 'Выберите сервис для сборки'
        )
    }

    environment {
        NEXUS_REGISTRY_URL = "${NEXUS_REGISTRY_URL}"
        DOCKER_BUILDKIT    = '1'
        // имя установки сканера из Global Tool Configuration
        SONAR_SCANNER_HOME = tool 'SonarScanner'
    }

    stages {
        stage('Determine service') {
            steps {
                script {
                    def webhookRepoName = (env.webhookRepoName ?: '').trim()
                    def paramService    = (params.PARAM_SERVICE ?: '').trim()
                    def finalService = webhookRepoName ? webhookRepoName : paramService

                    if (!finalService) {
                        error("SERVICE_NAME не задан: ни webhook (repository.name), ни параметр PARAM_SERVICE не переданы.")
                    }

                    env.SERVICE_NAME = finalService
                    echo "Using SERVICE_NAME=${env.SERVICE_NAME}"
                    def repoUrl = "http://gitlab:8060/ostapkob/${env.SERVICE_NAME}"
                    git(
                        url: repoUrl,
                        branch: 'master',
                        credentialsId: 'gitlab-token'
                    )
                }
            }
        }

        stage('Checkout') {
            steps {
                script {
                    def repoUrl = "http://gitlab:8060/ostapkob/${env.SERVICE_NAME}"
                    git(
                        url: repoUrl,
                        branch: 'master',
                        credentialsId: 'gitlab-token'
                    )
                }
            }
        }

        stage('Build & Test') {
            steps {
                script {
                    sh 'docker version'
                    def testImage    = "${env.SERVICE_NAME}:test"
                    env.TEST_IMAGE   = testImage
                    sh "docker buildx build -f Dockerfile.test -t ${testImage} ."
                }
            }
        }

        stage('Run tests') {
            steps {
                // FIX: rm env 
                sh '''
                    env | grep -E "(POSTGRES|MINIO)" > /tmp/envfile
                    docker run --rm \
                      --env-file /tmp/envfile \
                      --add-host minio:$MINIO_IP \
                      --add-host postgres:$POSTGRES_IP \
                      --add-host kafka:$KAFKA_IP \
                      ${TEST_IMAGE}
                '''
            }
        }

        stage('SonarQube analysis') {
            steps {
                script {
                    withSonarQubeEnv('SonarQubeLocal') {
                        sh "${SONAR_SCANNER_HOME}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Quality Gate') {
            when {
                expression { return env.CHANGE_ID == null } // по желанию, например только на merge
            }
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build release image') {
            steps {
                script {
                    def releaseImage = "${env.NEXUS_REGISTRY_URL}/${env.SERVICE_NAME}:${env.BUILD_NUMBER}"
                    env.RELEASE_IMAGE = releaseImage
                    sh "docker buildx build -f Dockerfile -t ${releaseImage} ."
                }
            }
        }

        stage('Push to Nexus') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'nexus-docker-creds',
                    usernameVariable: 'NEXUS_USER',
                    passwordVariable: 'NEXUS_PASS'
                )]) {
                    println("NEXUS_REGISTRY_URL: ${env.NEXUS_REGISTRY_URL}")
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

