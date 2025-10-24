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
                        # Создаем виртуальное окружение и устанавливаем зависимости
                        python3 -m venv /tmp/venv
                        . /tmp/venv/bin/activate
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        
        stage('Wait for BMC') {
            steps {
                script {
                    echo "Waiting for BMC to be ready..."
                    sh '''
                        . /tmp/venv/bin/activate
                        python3 wait_for_bmc.py
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    echo "Running OpenBMC tests..."
                    sh '''
                        . /tmp/venv/bin/activate
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
