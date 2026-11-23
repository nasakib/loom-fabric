"""
Deploy and synchronize Universal JIT & ClothOS update across the Ray cluster.
Transfers updated source files and runs verification on remote node WIN-7CMAQLVP8MV (192.168.99.2).
"""

import os
import sys
import json
import socket
from pathlib import Path
import ray

LOCAL_UJIT_DIR = Path(r"c:\Users\natsa\Documents\universal-jit")
LOCAL_LOOM_DIR = Path(r"c:\Users\natsa\Documents\loom-fabric")

def collect_files():
    payload = {
        "universal_jit": {},
        "loom_fabric": {}
    }

    # Universal JIT files
    ujit_rel_paths = [
        "include/ujit.h",
        "src/internal.h",
        "src/parser.c",
        "src/opt.c",
        "src/emitter_x86.c",
        "src/runtime.c",
        "bindings/python/setup.py",
        "bindings/python/ujit/__init__.py",
        "bindings/python/ujit/native_compiler.py",
        "adapters/clothos/clothos_ujit.py",
        "adapters/minivm/minivm_ujit.c",
        "Makefile",
        "README.md",
    ]
    for rel in ujit_rel_paths:
        p = LOCAL_UJIT_DIR / rel
        if p.exists():
            payload["universal_jit"][rel] = p.read_text(encoding="utf-8")

    # Loom Fabric files
    loom_rel_paths = [
        "clothos_root/bin/ujit",
        "tests/test_clothos_ujit_integration.py",
    ]
    # Add all loom/{clothos, stitch, genetics, tools}/*.py files
    for subdir in ["clothos", "stitch", "genetics", "tools"]:
        d = LOCAL_LOOM_DIR / "loom" / subdir
        if d.exists():
            for py_file in d.glob("*.py"):
                rel = f"loom/{subdir}/{py_file.name}"
                loom_rel_paths.append(rel)

    for rel in loom_rel_paths:
        p = LOCAL_LOOM_DIR / rel
        if p.exists():
            payload["loom_fabric"][rel] = p.read_text(encoding="utf-8")

    return payload


@ray.remote
def deploy_to_remote_node(payload: dict) -> dict:
    hostname = socket.gethostname()
    results = []

    remote_ujit = Path(r"C:\Users\natsa\Documents\universal-jit")
    remote_loom = Path(r"C:\Users\natsa\Documents\loom-fabric")

    # 1. Deploy Universal JIT
    for rel_path, content in payload["universal_jit"].items():
        target = remote_ujit / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        results.append(f"Wrote {target}")

    # 2. Deploy Loom Fabric updates
    for rel_path, content in payload["loom_fabric"].items():
        target = remote_loom / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        results.append(f"Wrote {target}")

    # 3. Run remote verification test
    test_file = remote_loom / "tests" / "test_clothos_ujit_integration.py"
    import subprocess
    remote_python = r"C:\Users\natsa\Documents\loom-fabric\.venv\Scripts\python.exe"
    if not os.path.exists(remote_python):
        remote_python = sys.executable

    clean_env = os.environ.copy()
    clean_env.pop("PYTHONHOME", None)
    clean_env.pop("PYTHONPATH", None)
    clean_env.pop("VIRTUAL_ENV", None)

    cmd = [
        remote_python,
        str(test_file)
    ]
    try:
        run_res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(remote_loom), env=clean_env, timeout=30)
        returncode = run_res.returncode
        stdout = run_res.stdout
        stderr = run_res.stderr
    except subprocess.TimeoutExpired:
        returncode = -1
        stdout = ""
        stderr = "Test timed out after 30 seconds"
    except Exception as e:
        returncode = -2
        stdout = ""
        stderr = str(e)

    return {
        "hostname": hostname,
        "files_synced": len(results),
        "test_returncode": returncode,
        "test_stdout": stdout,
        "test_stderr": stderr,
    }


def main():
    print("Collecting files for cluster deployment...")
    payload = collect_files()
    print(f"Universal JIT files: {len(payload['universal_jit'])}")
    print(f"Loom Fabric files:   {len(payload['loom_fabric'])}")

    print("\nConnecting to Ray cluster head (192.168.99.2:6379)...")
    ray.init(address="192.168.99.2:6379", ignore_reinit_error=True)

    print("\n[+] Deploying & Verifying across BOTH physical ClothOS nodes:")
    print("  -> Node 1: skyTech (192.168.99.1 - Local Silicon / RTX 3060)")
    print("  -> Node 2: WIN-7CMAQLVP8MV (192.168.99.2 - Remote Ray Cluster Head / Ryzen 7)")

    # Dispatch to Node 1 explicitly
    future_node1 = deploy_to_remote_node.options(resources={"node:192.168.99.1": 0.01}).remote(payload)
    # Dispatch to Node 2 explicitly
    future_node2 = deploy_to_remote_node.options(resources={"node:192.168.99.2": 0.01}).remote(payload)

    res_node1 = ray.get(future_node1)
    res_node2 = ray.get(future_node2)

    for res in [res_node1, res_node2]:
        print("\n================ CLUSTER NODE DEPLOYMENT REPORT ================")
        print(f"Target Hostname:    {res['hostname']}")
        print(f"Files Synchronized: {res['files_synced']}")
        print(f"Test Exit Code:     {res['test_returncode']}")
        print("\nNode Test Output:")
        print(res["test_stdout"].strip())
        if res["test_stderr"]:
            print("Node Test Errors:")
            print(res["test_stderr"].strip())
        print("================================================================")

    if res_node1["test_returncode"] == 0 and res_node2["test_returncode"] == 0:
        print("\n>>> CLUSTER UPDATE FULLY INSTALLED AND VERIFIED ACROSS BOTH SYSTEMS! <<<")
    else:
        print("\n[!] One or more cluster nodes failed verification.")


if __name__ == "__main__":
    main()
