import json
import urllib.request

dl_cmd = 'Invoke-WebRequest -Uri "http://192.168.99.1:5555/api/storage/file/laptop_openclaw.json" -Headers @{"X-Fabric-Token"="G-GzcZEzqteW241i720XeH5UNT73T6qk"} -OutFile "C:\\Users\\natsa\\.openclaw\\openclaw.json"'

payload = {
    "command": dl_cmd,
    "target_node": "local",
    "require_approval": False,
    "timeout_sec": 15
}

req = urllib.request.Request(
    "http://192.168.99.2:5555/api/admin/exec",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json", "X-Fabric-Token": "G-GzcZEzqteW241i720XeH5UNT73T6qk"}
)

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("Laptop Sync Result:", resp.read().decode())
except Exception as e:
    print("Error:", e)
