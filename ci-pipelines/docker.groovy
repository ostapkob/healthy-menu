pipeline {
    agent any

    environment {
        PATH = "${env.PATH}:/home/jenkins/.local/bin"
    }

    stages {
        stage('Test docker') {
            steps {
                sh '''
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                               docker:27.3-cli-alpine docker version
                '''
            }
        }


    }
    
}

