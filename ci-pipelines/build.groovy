pipeline {
    agent any
    
    parameters {
        string(name: 'NAME', defaultValue: 'World', description: 'Input your name')
    }

    stages {
        stage('Preparation') {
            steps {
                script {
                    echo "Preparing for build..."
                    // Здесь можно добавить дополнительные шаги подготовки
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    echo "Hello, ${params.NAME}!" // Используем введенное имя
                    echo "-------------------------" // Используем введенное имя
                    // Здесь может быть код сборки, например, компиляция проекта
                }
            }
        }

        stage('Post-Build Actions') {
            steps {
                script {
                    echo "Build completed successfully."
                    // Здесь могут быть действия после сборки, например, уведомления или артефакты
                }
            }
        }
    }
}

