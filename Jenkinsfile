pipeline {
    agent any
    
    environment {
        BMC_URL = 'https://localhost:2443'
        BMC_USERNAME = 'root'
        BMC_PASSWORD = '0penBmc'
    }
    
    options {
        timeout(time: 15, unit: 'MINUTES')
    }
    
    stages {
        stage('Setup Environment') {
            steps {
                script {
                    echo "Setting up Python environment..."
                    sh '''
                        # Устанавливаем необходимые пакеты
                        apt-get update && apt-get install -y python3-full python3-pip
                        # Устанавливаем зависимости напрямую
                        pip3 install -r requirements.txt --break-system-packages
                    '''
                }
            }
        }
        
        stage('Wait for BMC') {
            steps {
                script {
                    echo "Waiting for BMC to be ready..."
                    sh 'python3 wait_for_bmc.py'
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    echo "Running OpenBMC tests..."
                    sh '''
                        mkdir -p test-results
                        python3 run_tests.py --all
                    '''
                }
            }
            post {
                always {
                    junit 'test-results/*.xml'
                    archiveArtifacts artifacts: 'test-results/**/*'
                }
            }
        }
    }
    
    post {
        always {
            echo "Build completed - check test results in artifacts"
        }
        success {
            echo "✅ All tests passed!"
        }
        failure {
            echo "❌ Some tests failed"
        }
    }
}
