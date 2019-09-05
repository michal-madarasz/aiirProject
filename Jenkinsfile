pipeline {
    agent any
    stages {
        stage('run') {
            docker-compose up
        }
    }
    post {
        success {
            echo 'Success'
        }
        failure {
            echo 'Failed'
        }
    }
}
