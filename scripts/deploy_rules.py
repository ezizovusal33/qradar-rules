import os
import requests
import zipfile
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_IP = os.getenv("QRADAR_IP")
QRADAR_TOKEN = os.getenv("QRADAR_TOKEN")

zip_filename = 'qradar_rules_package.zip'

# 1. QRadar-ın tələb etdiyi manifest.xml məzmununu yaradırıq
manifest_content = """<?xml version="1.0" encoding="UTF-8"?>
<extension manifest_version="1.0" name="Custom_SOC_Rules" description="Automated Detection-as-Code Rules">
    <creates>
        <content_type name="CustomRule">
"""

# rules qovluğundakı XML fayllarını oxuyub manifest-ə əlavə edirik və ZIP-ə yığırıq
xml_files = []
if os.path.exists('rules'):
    for root, dirs, files in os.walk('rules'):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(file)

for file in xml_files:
    manifest_content += f'            <file name="{file}" />\n'

manifest_content += """        </content_type>
    </creates>
</extension>
"""

# 2. ZIP paketini yaradırıq və içinə hem manifest.xml, həm də XML rule-ları əlavə edirik
with zipfile.ZipFile(zip_filename, 'w') as zipf:
    # Manifest faylını yazırıq
    zipf.writestr('manifest.xml', manifest_content)
    
    # Rule XML fayllarını əlavə edirik
    for root, dirs, files in os.walk('rules'):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root, file)
                zipf.write(file_path, file)

print(f"[+] {zip_filename} manifest.xml ilə birlikdə uğurla yaradıldı.")

# 3. QRadar Extension Management API-yə POST sorğusu göndəririk
url = f"https://{QRADAR_IP}/api/config/extension_management/extensions"
headers = {
    "SEC": QRADAR_TOKEN,
    "Content-Type": "application/zip"
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