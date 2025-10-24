#!/usr/bin/env python3
import requests
import time
import os
import sys

def wait_for_bmc():
    bmc_url = os.getenv('BMC_URL', 'https://localhost:2443')
    username = os.getenv('BMC_USERNAME', 'root')
    password = os.getenv('BMC_PASSWORD', '0penBmc')
    
    print(f"Waiting for BMC at {bmc_url}...")
    
    for i in range(30):  # 5 minutes max
        try:
            response = requests.get(
                f"{bmc_url}/redfish/v1/",
                auth=(username, password),
                verify=False,
                timeout=5
            )
            if response.status_code == 200:
                print("✅ BMC is ready!")
                return True
        except Exception:
            pass
        
        if i % 5 == 0:
            print(f"Still waiting... ({i*10}s)")
        time.sleep(10)
    
    print("❌ Timeout waiting for BMC")
    return False

if __name__ == "__main__":
    success = wait_for_bmc()
    sys.exit(0 if success else 1)
