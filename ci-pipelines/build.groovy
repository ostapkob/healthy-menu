pipeline {
    agent { label 'linux' }

    environment {
        PATH = "${env.PATH}:/home/jenkins/.local/bin"
    }

    stages {
        stage('Checkout') {
            steps {
                git(
                    url: 'http://gitlab:8060/ostapkob/admin-backend',
                    branch: 'master',
                    credentialsId: 'ostapkob'
                )
            }
        }

        stage('Setup') {
            steps {
                sh '''
                    which uv || curl -LsSf https://astral.sh/uv/install.sh | sh
                '''
            }
        }

        stage('Test') {
            steps {
                dir('admin-backend') {
                    sh '''
                        mkdir -p test-results
                        uv sync
                        uv run coverage run --source=. -m pytest tests/ --junitxml=test-results/results.xml
                        uv run coverage xml --include="*" -o test-results/coverage.xml
                        ls -la test-results/  # Для отладки
                    '''
                }
            }
            post {
                always {
                    dir('admin-backend') {
                        script {
                            if (fileExists('test-results/results.xml')) {
                                junit testResults: 'test-results/results.xml', allowEmptyResults: false
                            } else {
                                echo 'JUnit XML file not found, skipping JUnit report'
                            }
                        }
                        recordCoverage tools: [
                            [parser: 'COBERTURA', pattern: 'test-results/coverage.xml']
                        ]
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

