import os
import requests
import zipfile
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_IP = os.getenv("QRADAR_IP")
QRADAR_TOKEN = os.getenv("QRADAR_TOKEN")

# 1. rules/ qovluğundakı bütün XML rule-ları ZIP paketinə yığırıq
zip_filename = 'qradar_rules_package.zip'
with zipfile.ZipFile(zip_filename, 'w') as zipf:
    for root, dirs, files in os.walk('rules'):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root, file)
                zipf.write(file_path, file)

print(f"[+] {zip_filename} uğurla yaradıldı.")

# 2. QRadar Extension Management API-yə POST sorğusu göndəririk
url = f"https://{QRADAR_IP}/api/config/extension_management/extensions"
headers = {
    "SEC": QRADAR_TOKEN,
    "Content-Type": "application/octet-stream"
}

with open(zip_filename, 'rb') as f:
    response = requests.post(url, headers=headers, data=f, verify=False)

print(f"[-] QRadar API Status Code: {response.status_code}")
print(f"[-] Response: {response.text}")

if response.status_code in [200, 201, 202]:
    print("[+] Rule-lar QRadar-a uğurla deploy olundu!")
else:
    print("[!] Deploy zamanı xəta baş verdi.")
    exit(1)