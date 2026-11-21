import urllib.request
import urllib.error
import json

endpoints = [
    ("GET", "/api/os/hal", None),
    ("GET", "/api/os/processes", None),
    ("GET", "/api/os/vfs/tree?path=%2F", None),
    ("POST", "/api/os/shell/exec", {"command": "hal", "cwd": "/"}),
    ("GET", "/api/telemetry/taskmanager", None),
    ("GET", "/api/telemetry/sse?interval=0.1", None),
    ("GET", "/api/cluster/ports", None),
    ("GET", "/api/ports/audit", None),
    ("GET", "/api/si/focus/state", None),
    ("GET", "/api/si/comm/feed", None),
    ("GET", "/api/zmq/recent", None),
    ("GET", "/api/status", None),
]

for method, path, body in endpoints:
    url = f"http://127.0.0.1:8087{path}"
    headers = {"User-Agent": "TabChecker"}
    data = None
    if body:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            content_type = resp.headers.get_content_type()
            raw = resp.read()
            first_chars = raw[:30].decode("utf-8", errors="replace")
            print(f"[{resp.status}] {method} {path} | Content-Type: {content_type} | Start: {first_chars!r}")
            if "json" in content_type:
                try:
                    parsed = json.loads(raw)
                    # print("   Parsed JSON ok")
                except Exception as e:
                    print(f"   >>> JSON PARSE ERROR: {e} <<<")
            elif raw.strip().startswith(b"<"):
                print(f"   >>> RETURNED HTML: starts with '<' ! <<<")
    except urllib.error.HTTPError as e:
        raw = e.read()
        first_chars = raw[:30].decode("utf-8", errors="replace")
        print(f"[{e.code}] {method} {path} | Error: {e.reason} | Start: {first_chars!r}")
        if raw.strip().startswith(b"<"):
            print(f"   >>> RETURNED HTML ON ERROR: starts with '<' ! <<<")
    except Exception as e:
        print(f"[ERR] {method} {path} | {e}")
