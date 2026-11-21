import re
import urllib.request
import urllib.error

content = open('loom/fabric/dashboard_server.py', encoding='utf-8').read()
matches = re.findall(r'fetch\([`\'"](/api/[^`\'"?]+)', content)
urls = sorted(set(matches))
print(f"Found {len(urls)} distinct API endpoints in frontend JavaScript:")

for url in urls:
    full_url = f"http://127.0.0.1:8087{url}"
    try:
        req = urllib.request.Request(full_url, headers={'User-Agent': 'EndpointChecker'})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            content_type = resp.headers.get_content_type()
            status = resp.status
            if "json" not in content_type:
                print(f"[NON-JSON!] {url} -> status={status}, content_type={content_type}")
            else:
                # print(f"[OK] {url}")
                pass
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {url} -> {e.reason}")
    except Exception as e:
        print(f"[ERR] {url} -> {e}")
