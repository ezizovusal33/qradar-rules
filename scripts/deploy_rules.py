import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_IP = os.getenv("QRADAR_IP")
QRADAR_TOKEN = os.getenv("QRADAR_TOKEN")

# QRadar Rule Management API endpoint
url = f"https://{QRADAR_IP}/api/config/ame/rules"
headers = {
    "SEC": QRADAR_TOKEN,
    "Content-Type": "application/xml",
    "Accept": "application/json"
}

success_count = 0
fail_count = 0

if os.path.exists('rules'):
    for root, dirs, files in os.walk('rules'):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root, file)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    xml_data = f.read()
                
                # QRadar-a tək-tək POST sorğusu göndəririk
                response = requests.post(url, headers=headers, data=xml_data.encode('utf-8'), verify=False)
                
                if response.status_code in [200, 201, 202]:
                    print(f"[+] Uğurla deploy olundu: {file}")
                    success_count += 1
                else:
                    print(f"[!] Xəta ({file}) - Status Code: {response.status_code}")
                    print(f"    Response: {response.text}")
                    fail_count += 1

print(f"\nDeploy yekunlaşdı. Uğurlu: {success_count}, Xətalı: {fail_count}")

if fail_count > 0:
    exit(1)