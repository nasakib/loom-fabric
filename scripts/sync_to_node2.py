import os
import sys
import time

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"

from ray.job_submission import JobSubmissionClient, JobStatus

def sync():
    print("Connecting to Ray Cluster on Node 2 (100.74.98.21:8265)...")
    client = JobSubmissionClient("http://100.74.98.21:8265")
    
    job_id = client.submit_job(
        entrypoint="python -c \"import loom; print('Node 2 Sync Verification: Success')\"",
        runtime_env={
            "working_dir": ".",
            "excludes": [
                ".git", "node_modules", ".venv", "__pycache__", ".pnpm-store",
                "apps", "artifacts", "deliverables", "sovereign_vault", "vault",
                "traces", "interpretations", "clothos_root", "bin", ".agent",
                ".loom_hypotheses.db", "*.db", "*.sqlite", "*.db-wal", "*.db-shm"
            ]
        }
    )
    print(f"Submitted sync job: {job_id}")
    
    # Wait for completion
    for _ in range(30):
        status = client.get_job_status(job_id)
        if status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED]:
            print(f"Job {job_id} finished with status: {status}")
            logs = client.get_job_logs(job_id)
            print("Logs:", logs)
            break
        time.sleep(1)

if __name__ == "__main__":
    sync()
