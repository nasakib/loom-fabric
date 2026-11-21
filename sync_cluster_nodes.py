"""
Cross-Node Synchronization Script for Loom Fabric & OpenClaw.
Syncs configuration, provider extensions, and models between skyTech (192.168.99.1)
and WIN-7CMAQLVP8MV (192.168.99.2) via Ray distributed runtime.
"""

import os
import sys
import json
import socket
import subprocess
import ray

def main():
    print("Initializing Ray connection to cluster head (192.168.99.2:6379)...")
    ray.init(address='192.168.99.2:6379', ignore_reinit_error=True)

    # 1. Read local files to sync
    with open(r'C:\Users\natsa\AppData\Roaming\npm\node_modules\openclaw\dist\extensions\loom-fabric\openclaw.plugin.json', 'r', encoding='utf-8') as f:
        plugin_json_content = f.read()

    with open(r'C:\Users\natsa\AppData\Roaming\npm\node_modules\openclaw\dist\extensions\loom-fabric\index.js', 'r', encoding='utf-8') as f:
        index_js_content = f.read()

    with open(r'C:\Users\natsa\AppData\Roaming\npm\node_modules\openclaw\dist\extensions\loom-fabric\package.json', 'r', encoding='utf-8') as f:
        package_json_content = f.read()

    with open(r'C:\Users\natsa\.openclaw\openclaw.json', 'r', encoding='utf-8') as f:
        openclaw_json_dict = json.load(f)

    # On remote node, baseUrl should point to 192.168.99.1:8002 if gateway is hosted on skyTech
    openclaw_json_dict['models']['providers']['loom-fabric']['baseUrl'] = 'http://192.168.99.1:8002/v1'
    remote_openclaw_json_content = json.dumps(openclaw_json_dict, indent=2)

    @ray.remote
    def sync_remote_node(plugin_json, index_js, pkg_json, openclaw_json):
        host = socket.gethostname()
        results = []

        # 1. Update openclaw.json
        oc_path = os.path.expanduser('~/.openclaw/openclaw.json')
        with open(oc_path, 'w', encoding='utf-8') as f:
            f.write(openclaw_json)
        results.append(f"Updated {oc_path}")

        # Also update last-good
        with open(oc_path + '.last-good', 'w', encoding='utf-8') as f:
            f.write(openclaw_json)

        # 2. Extension directories
        dirs = [
            os.path.expanduser(r'~\AppData\Roaming\npm\node_modules\openclaw\dist\extensions\loom-fabric'),
            os.path.expanduser(r'~/.openclaw/extensions/loom-fabric'),
            os.path.expanduser(r'~/.openclaw/npm/node_modules/@openclaw/loom-fabric')
        ]

        for d in dirs:
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, 'openclaw.plugin.json'), 'w', encoding='utf-8') as f:
                f.write(plugin_json)
            with open(os.path.join(d, 'index.js'), 'w', encoding='utf-8') as f:
                f.write(index_js)
            with open(os.path.join(d, 'package.json'), 'w', encoding='utf-8') as f:
                f.write(pkg_json)
            results.append(f"Synced extension to {d}")

        # 3. Restart OpenClaw Gateway on remote node if scheduled task exists
        try:
            cmd = "Stop-ScheduledTask -TaskName 'OpenClaw Gateway' -ErrorAction SilentlyContinue; Start-Sleep -Seconds 1; Start-ScheduledTask -TaskName 'OpenClaw Gateway' -ErrorAction SilentlyContinue"
            subprocess.run(['powershell', '-Command', cmd], timeout=10)
            results.append(f"Restarted OpenClaw Gateway scheduled task on {host}")
        except Exception as e:
            results.append(f"Restart note: {e}")

        return {'host': host, 'results': results}

    f = sync_remote_node.remote(plugin_json_content, index_js_content, package_json_content, remote_openclaw_json_content)
    res = ray.get(f)
    print("SYNC RESULTS FROM REMOTE NODE:")
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
