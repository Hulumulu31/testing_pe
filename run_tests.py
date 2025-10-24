#!/usr/bin/env python3
"""
OpenBMC CI/CD Test Runner - FINAL VERSION
"""

import subprocess
import sys
import os
import time
import requests
import urllib3
import json
import argparse
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OpenBMCTestRunner:
    def __init__(self):
        self.bmc_url = os.getenv('BMC_URL', 'https://localhost:2443')
        self.bmc_username = os.getenv('BMC_USERNAME', 'root')
        self.bmc_password = os.getenv('BMC_PASSWORD', '0penBmc')
        self.test_results = []
        
    def wait_for_bmc_ready(self, timeout=300):
        """Wait for BMC to be ready"""
        print("⏳ Waiting for OpenBMC to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(
                    f"{self.bmc_url}/redfish/v1/",
                    auth=(self.bmc_username, self.bmc_password),
                    verify=False,
                    timeout=10
                )
                if response.status_code == 200:
                    print("✅ OpenBMC is ready!")
                    return True
            except Exception as e:
                print(f"❌ BMC not ready yet: {e}")
            
            time.sleep(10)
        
        print("⏰ Timeout waiting for BMC")
        return False
    
    def run_basic_connection_test(self):
        """Basic connection test for OpenBMC"""
        print("🔌 Running basic connection tests...")
        try:
            session = requests.Session()
            session.auth = (self.bmc_username, self.bmc_password)
            session.verify = False
            
            tests_passed = 0
            total_tests = 3
            
            # Test 1: Service Root
            response = session.get(f"{self.bmc_url}/redfish/v1/")
            if response.status_code == 200:
                print("✅ Service Root: Connected")
                tests_passed += 1
            else:
                print(f"❌ Service Root: Failed with status {response.status_code}")
                return False
            
            # Test 2: System Info
            response = session.get(f"{self.bmc_url}/redfish/v1/Systems/system")
            if response.status_code == 200:
                data = response.json()
                power_state = data.get('PowerState', 'Unknown')
                print(f"✅ System Info: PowerState={power_state}")
                tests_passed += 1
            else:
                print(f"❌ System Info: Failed with status {response.status_code}")
                return False
            
            # Test 3: Managers collection
            response = session.get(f"{self.bmc_url}/redfish/v1/Managers")
            if response.status_code == 200:
                print("✅ Managers: Accessible")
                tests_passed += 1
            else:
                print(f"⚠️ Managers: Status {response.status_code}")
            
            print(f"📊 Basic connection: {tests_passed}/{total_tests} tests passed")
            return tests_passed >= 2
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

    def run_api_tests_with_pytest(self):
        """Run comprehensive API tests using pytest"""
        print("🔧 Running API tests with pytest...")
        try:
            # Create comprehensive API test file
            test_content = '''
import pytest
import requests
import os
import json

class TestOpenBMCAPI:
    """Comprehensive OpenBMC API tests"""
    
    @pytest.fixture
    def session(self):
        session = requests.Session()
        session.auth = (os.getenv("BMC_USERNAME", "root"), os.getenv("BMC_PASSWORD", "0penBmc"))
        session.verify = False
        return session
    
    @pytest.fixture
    def bmc_url(self):
        return os.getenv("BMC_URL", "https://localhost:2443")
    
    def test_service_root(self, session, bmc_url):
        """Test Redfish Service Root"""
        response = session.get(bmc_url + "/redfish/v1/")
        assert response.status_code == 200
        data = response.json()
        assert "RedfishVersion" in data or "Version" in data
        assert "Systems" in data
    
    def test_systems_collection(self, session, bmc_url):
        """Test Systems collection"""
        response = session.get(bmc_url + "/redfish/v1/Systems")
        assert response.status_code == 200
        data = response.json()
        assert "Members" in data
    
    def test_system_instance(self, session, bmc_url):
        """Test specific System instance"""
        response = session.get(bmc_url + "/redfish/v1/Systems/system")
        assert response.status_code == 200
        data = response.json()
        assert "PowerState" in data or "Status" in data
    
    def test_managers_collection(self, session, bmc_url):
        """Test Managers collection"""
        response = session.get(bmc_url + "/redfish/v1/Managers")
        assert response.status_code == 200
        data = response.json()
        assert "Members" in data
'''
            # Write test file
            with open('openbmc_api_test.py', 'w') as f:
                f.write(test_content)
            
            # Run pytest with built-in JUnit XML reporting
            result = subprocess.run([
                'python3', '-m', 'pytest',
                'openbmc_api_test.py', '-v',
                '--junitxml=test-results/api-tests.xml',
                '--html=test-results/api-report.html',
                '--self-contained-html'
            ], capture_output=True, text=True, timeout=120)
            
            # Cleanup
            if os.path.exists('openbmc_api_test.py'):
                os.remove('openbmc_api_test.py')
            
            print(f"Pytest output: {result.stdout}")
            if result.stderr:
                print(f"Pytest errors: {result.stderr}")
            
            if result.returncode == 0:
                print("✅ API tests passed")
                return True
            else:
                print(f"❌ API tests failed with return code: {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ API tests timed out")
            return False
        except Exception as e:
            print(f"❌ API tests error: {e}")
            return False

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive OpenBMC CI/CD Test Suite")
        print(f"BMC URL: {self.bmc_url}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Create test results directory
        os.makedirs('test-results', exist_ok=True)
        
        # Wait for BMC to be ready
        if not self.wait_for_bmc_ready():
            print("❌ Cannot proceed - BMC is not ready")
            return False
        
        # Define test suites
        test_suites = [
            ("Basic Connection", self.run_basic_connection_test),
            ("API Tests", self.run_api_tests_with_pytest),
        ]
        
        all_passed = True
        for test_name, test_func in test_suites:
            try:
                print(f"\n🎯 EXECUTING: {test_name}")
                print("-" * 40)
                success = test_func()
                self.test_results.append((test_name, success))
                if not success:
                    all_passed = False
                    print(f"❌ {test_name} FAILED")
                else:
                    print(f"✅ {test_name} PASSED")
            except Exception as e:
                print(f"💥 ERROR in {test_name}: {e}")
                self.test_results.append((test_name, False))
                all_passed = False
        
        # Generate final report
        print("\n" + "=" * 60)
        print("📊 GENERATING FINAL TEST REPORT")
        print("=" * 60)
        
        passed = sum(1 for _, success in self.test_results if success)
        total = len(self.test_results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"📈 TOTAL: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 EXCELLENT: All tests passed!")
        elif success_rate >= 80:
            print("👍 GOOD: Most tests passed")
        elif success_rate >= 60:
            print("⚠️  FAIR: Some tests failed")
        else:
            print("❌ POOR: Many tests failed")
        
        print(f"🏁 Test execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💾 Test results saved in: test-results/")
        
        return all_passed

def main():
    parser = argparse.ArgumentParser(description='OpenBMC Test Runner')
    parser.add_argument('--basic', action='store_true', help='Run basic connection tests')
    parser.add_argument('--api', action='store_true', help='Run API tests')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    
    args = parser.parse_args()
    
    runner = OpenBMCTestRunner()
    
    # Create test results directory
    os.makedirs('test-results', exist_ok=True)
    
    if args.all or not any(vars(args).values()):
        # Run all tests
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)
    else:
        # Run specific tests
        if args.basic:
            runner.run_basic_connection_test()
        if args.api:
            runner.run_api_tests_with_pytest()

if __name__ == "__main__":
    main()
