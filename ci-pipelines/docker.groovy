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
            causeString: 'GitLab MR ($webhookMrState) for $webbotProjectNs',
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
        NEXUS_REGISTRY_URL = "${NEXUS_REGISTRY_URL}"
        DOCKER_BUILDKIT    = '1'
        SONAR_HOST_URL     = 'http://localhost:9090'
        SONAR_AUTH_TOKEN   = credentials('sonar-token')
        SONAR_SCANNER_OPTS = "-Dproject.settings=sonar-project.properties"
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
                    
                    // Определяем тип сервиса
                    if (env.SERVICE_NAME.contains('frontend')) {
                        env.SERVICE_TYPE = 'frontend'
                        env.LANGUAGE = 'javascript'
                        env.BUILD_TOOL = 'npm'
                    } else if (env.SERVICE_NAME.contains('backend')) {
                        env.SERVICE_TYPE = 'backend'
                        env.LANGUAGE = 'python'
                        env.BUILD_TOOL = 'pip'
                    }
                    
                    echo "Using SERVICE_NAME=${env.SERVICE_NAME}, TYPE=${env.SERVICE_TYPE}"
                    
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
                script {
                    // Разные команды для frontend и backend
                    if (env.SERVICE_TYPE == 'frontend') {
                        sh '''
                            docker run --rm \
                                -v "${WORKSPACE}:/app" \
                                -w /app \
                                node:16-alpine \
                                sh -c "npm ci && npm test -- --coverage"
                            
                            # Копируем отчет о покрытии из контейнера
                            docker create --name test-container ${TEST_IMAGE}
                            docker cp test-container:/app/coverage ./coverage || true
                            docker rm test-container
                        '''
                    } else if (env.SERVICE_TYPE == 'backend') {
                        sh '''
                            env | grep -E "(POSTGRES|MINIO)" > /tmp/envfile
                            docker run --rm \
                                --env-file /tmp/envfile \
                                --add-host minio:${FEDORA} \
                                --add-host postgres:${FEDORA} \
                                --add-host kafka:${FEDORA} \
                                -v "${WORKSPACE}:/app" \
                                ${TEST_IMAGE}
                            
                            # Генерируем отчет о покрытии для Python (если используется pytest-cov)
                            docker run --rm \
                                -v "${WORKSPACE}:/app" \
                                -w /app \
                                python:3.9-slim \
                                sh -c "pip install pytest pytest-cov && pytest --cov=. --cov-report=xml:coverage.xml" || true
                        '''
                    }
                }
            }
        }

        // Подготовка SonarQube для разных языков
        stage('Configure SonarQube Analysis') {
            steps {
                script {
                    def projectKey = "${env.SERVICE_NAME}-${env.BUILD_NUMBER}"
                    
                    if (env.SERVICE_TYPE == 'frontend') {
                        // Для Svelte/JavaScript проектов
                        writeFile file: 'sonar-project.properties', text: """
                        sonar.projectKey=${projectKey}
                        sonar.projectName=${env.SERVICE_NAME}
                        sonar.projectVersion=1.0
                        sonar.sources=src
                        sonar.tests=src
                        sonar.test.inclusions=**/*.test.js,**/*.spec.js
                        sonar.javascript.lcov.reportPaths=coverage/lcov.info
                        sonar.exclusions=node_modules/**,dist/**,coverage/**,**/*.spec.js
                        sonar.sourceEncoding=UTF-8
                        sonar.host.url=${env.SONAR_HOST_URL}
                        sonar.login=${env.SONAR_AUTH_TOKEN}
                        """
                        
                        // Проверяем, есть ли отчет о покрытии
                        sh '''
                            if [ -f "coverage/lcov.info" ]; then
                                echo "Coverage report found"
                            else
                                echo "No coverage report, creating empty one"
                                mkdir -p coverage
                                echo "TN:" > coverage/lcov.info
                                echo "SF:" >> coverage/lcov.info
                            fi
                        '''
                        
                    } else if (env.SERVICE_TYPE == 'backend') {
                        // Для Python проектов
                        writeFile file: 'sonar-project.properties', text: """
                        sonar.projectKey=${projectKey}
                        sonar.projectName=${env.SERVICE_NAME}
                        sonar.projectVersion=1.0
                        sonar.sources=.
                        sonar.tests=tests
                        sonar.test.inclusions=**/test_*.py,**/*_test.py
                        sonar.python.coverage.reportPaths=coverage.xml
                        sonar.exclusions=**/migrations/**,**/__pycache__/**,**/*.pyc
                        sonar.sourceEncoding=UTF-8
                        sonar.host.url=${env.SONAR_HOST_URL}
                        sonar.login=${env.SONAR_AUTH_TOKEN}
                        sonar.python.version=3.9
                        """
                        
                        // Проверяем, есть ли отчет о покрытии
                        sh '''
                            if [ -f "coverage.xml" ]; then
                                echo "Coverage report found"
                            else
                                echo "No coverage report, creating empty one"
                                echo '<?xml version="1.0" ?><!DOCTYPE coverage SYSTEM "http://cobertura.sourceforge.net/xml/coverage-04.dtd"><coverage></coverage>' > coverage.xml
                            fi
                        '''
                    }
                }
            }
        }

        // Сканирование SonarQube
        stage('SonarQube Scan') {
            steps {
                script {
                    // Установка sonar-scanner в контейнере
                    def scannerImage = 'sonarsource/sonar-scanner-cli:latest'
                    
                    sh """
                        docker run --rm \
                            -v "${WORKSPACE}:/usr/src" \
                            -w /usr/src \
                            ${scannerImage}
                    """
                }
            }
        }

        // Ожидание Quality Gate
        stage('SonarQube Quality Gate Check') {
            steps {
                script {
                    timeout(time: 3, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }

        stage('Build release image') {
            steps {
                script {
                    def releaseImage = "${env.NEXUS_REGISTRY_URL}/${env.SERVICE_NAME}:${env.BUILD_NUMBER}"
                    env.RELEASE_IMAGE = releaseImage
                    
                    // Разные Dockerfile для frontend и backend
                    if (env.SERVICE_TYPE == 'frontend') {
                        sh "docker buildx build -f Dockerfile.prod -t ${releaseImage} ."
                    } else {
                        sh "docker buildx build -f Dockerfile -t ${releaseImage} ."
                    }
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
            // Сохраняем отчеты SonarQube
            archiveArtifacts artifacts: 'sonar-project.properties', allowEmptyArchive: true
            archiveArtifacts artifacts: 'coverage/**', allowEmptyArchive: true
            archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
            
            cleanWs()
        }
        success {
            script {
                echo "Сборка успешно завершена."
                if (env.SERVICE_TYPE) {
                    echo "Отчет SonarQube: ${SONAR_HOST_URL}/dashboard?id=${env.SERVICE_NAME}-${env.BUILD_NUMBER}"
                }
            }
        }
    }
}
