pipeline {
    agent any
    stages {
        stage('run') {
            steps {
                sh 'docker-compose up'
            }
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
