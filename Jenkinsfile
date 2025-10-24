pipeline {
    agent any
    
    environment {
        BMC_URL = 'https://localhost:2443'
        BMC_USERNAME = 'root'
        BMC_PASSWORD = '0penBmc'
        PYTHONPATH = '.'
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }
    
    stages {
        stage('Setup Environment') {
            steps {
                script {
                    echo "Setting up Python environment..."
                    sh 'python3 -m pip install --upgrade pip'
                    sh 'pip3 install -r requirements.txt'
                }
            }
        }
        
        stage('Start OpenBMC') {
            steps {
                script {
                    echo "Starting OpenBMC emulator..."
                    sh '''
                    # Запуск OpenBMC в фоновом режиме
                    cd /opt/openbmc
                    ./run-qemu.sh &
                    BMC_PID=$!
                    echo $BMC_PID > /tmp/bmc_pid
                    '''
                    
                    // Ждем готовности BMC
                    sleep time: 60, unit: 'SECONDS'
                }
            }
        }
        
        stage('Wait for BMC Ready') {
            steps {
                script {
                    echo "Waiting for BMC to be ready..."
                    sh 'python3 /opt/scripts/wait_for_bmc.py'
                }
            }
        }
        
        stage('Run Basic Connection Tests') {
            steps {
                script {
                    echo "Running basic connection tests..."
                    sh 'python3 /opt/scripts/run_tests.py --basic'
                }
            }
            post {
                always {
                    junit 'test-results/basic-connection.xml'
                }
            }
        }
        
        stage('Run API Tests') {
            steps {
                script {
                    echo "Running comprehensive API tests..."
                    sh 'python3 /opt/scripts/run_tests.py --api'
                }
            }
            post {
                always {
                    junit 'test-results/api-tests.xml'
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: false,
                        keepAll: true,
                        reportDir: 'test-results',
                        reportFiles: 'api-report.html',
                        reportName: 'API Test Report'
                    ])
                }
            }
        }
        
        stage('Run WebUI Tests') {
            steps {
                script {
                    echo "Running WebUI tests..."
                    sh 'python3 /opt/scripts/run_tests.py --webui'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'test-results/webui-*.png'
                }
            }
        }
        
        stage('Run Load Tests') {
            steps {
                script {
                    echo "Running load tests..."
                    sh 'python3 /opt/scripts/run_tests.py --load'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'test-results/load-test-results.json'
                }
            }
        }
        
        stage('Run Security Checks') {
            steps {
                script {
                    echo "Running security checks..."
                    sh 'python3 /opt/scripts/run_tests.py --security'
                }
            }
        }
        
        stage('Run Unit Tests') {
            steps {
                script {
                    echo "Running unit tests..."
                    sh 'python3 /opt/scripts/run_tests.py --unit'
                }
            }
            post {
                always {
                    junit 'test-results/unit-tests.xml'
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: false,
                        keepAll: true,
                        reportDir: 'test-results',
                        reportFiles: 'unit-report.html',
                        reportName: 'Unit Test Report'
                    ])
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "Cleaning up..."
                sh '''
                # Останавливаем BMC если он запущен
                if [ -f /tmp/bmc_pid ]; then
                    kill $(cat /tmp/bmc_pid) 2>/dev/null || true
                    rm -f /tmp/bmc_pid
                fi
                '''
            }
            
            // Сохраняем все артефакты
            archiveArtifacts artifacts: 'test-results/**/*'
            
            // Генерируем полный отчет
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'test-results',
                reportFiles: 'test-execution-report.json',
                reportName: 'Complete Test Report'
            ])
        }
        
        success {
            echo "All tests completed successfully!"
            emailext (
                subject: "SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: "All tests passed successfully.\n\nCheck console output at ${env.BUILD_URL}",
                to: "developer@example.com"
            )
        }
        
        failure {
            echo "Some tests failed!"
            emailext (
                subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: "Some tests failed.\n\nCheck console output at ${env.BUILD_URL}",
                to: "developer@example.com"
            )
        }
    }
}
