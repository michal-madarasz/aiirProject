pipeline {
    agent any
    stages {
        stage('run') {
            sh 'docker-compose up'
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
