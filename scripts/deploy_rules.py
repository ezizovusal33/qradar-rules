import os, sys, zipfile, glob, requests, urllib3

urllib3.disable_warnings()

HOST  = os.environ["QRADAR_IP"]
TOKEN = os.environ["QRADAR_TOKEN"]
BASE  = f"https://{HOST}/api"
H = {"SEC": TOKEN, "Version": "19.0", "Accept": "application/json"}

def build_package(rules_dir="qradar/rules", out="build/soc_custom_rules.zip"):
    os.makedirs("build", exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in glob.glob(f"{rules_dir}/*.xml"):
            z.write(f, arcname=os.path.basename(f))
        z.write("qradar/manifest.json", arcname="manifest.json")
    print(f"[+] ZIP paketi uğurla yaradıldı: {out}")
    return out

def upload(zip_path):
    with open(zip_path, "rb") as fh:
        r = requests.post(f"{BASE}/config/extension_management/extensions",
                          headers=H, files={"file": fh}, verify=False)
    if r.status_code not in (200, 201, 202):
        sys.exit(f"[!] Upload xətası {r.status_code}: {r.text}")
    ext_id = r.json()["id"]
    print(f"[+] Extension uğurla yükləndi. ID: {ext_id}")
    return ext_id

def install(ext_id):
    r = requests.post(f"{BASE}/config/extension_management/extensions/{ext_id}",
                      headers=H, params={"overwrite": "true", "status": "INSTALLED"},
                      verify=False)
    if r.status_code not in (200, 201, 202):
        sys.exit(f"[!] Install xətası {r.status_code}: {r.text}")
    print("[+] Extension uğurla quraşdırıldı (INSTALLED).")
    return r.json()

if __name__ == "__main__":
    z = build_package()
    ext_id = upload(z)
    install(ext_id)
    
    # Qaydaların (rules) aktivləşdirilməsi (enable)
    try:
        rules = requests.get(f"{BASE}/analytics/rules", headers=H, verify=False,
                             params={"filter": "name ILIKE 'SOC -%'"}).json()
        for r in rules:
            requests.post(f"{BASE}/analytics/rules/{r['id']}", headers=H, verify=False,
                          json={"enabled": True})
            print(f"[+] Aktivləşdirildi: {r['name']}")
    except Exception as e:
        print(f"[!] Rule status yenilənərkən xəta: {e}")