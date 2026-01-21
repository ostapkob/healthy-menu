pipeline {
    agent { label 'linux' }


    stages {

        stage('Checkout') {
            steps {
                git(
                    url: 'http://gitlab:8060/ostapkob/admin-backend',
                    branch: 'master', // или main, если у тебя так
                    credentialsId: 'ostapkob'
                    // glpat-mRM1-REoQY1cz6w6GPDUsG86MQp1OjMH.01.0w0dmwwlm
                )
            }
        }
        stage('Setup') {
            steps {
                    // # Установка uv (если не установлен)
                    sh '''
                        which uv || curl -LsSf https://astral.sh/uv/install.sh | sh
                        PATH=$PATH:/home/jenkins/.local/bin
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                dir ('admin-backend') {
                sh '''
                    # Активация окружения и запуск тестов
                    uv sync
                    uv run pytest tests/
                '''
                }
            }
            post {
                always {
                    junit 'test-results/*.xml'
                    cobertura 'coverage.xml'
                }
            }
        }


        
    }
    
    post {
        always {
            cleanWs()  # Очистка workspace
        }
    }




    
    }
}

