"""
Loom Fabric: Resumable GGUF Downloader with SHA-256 Verification.

Downloads architectural presets into ~/.loom/models with chunked streaming,
HTTP Range header resumption, and cryptographic integrity verification.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path
import httpx
from rich.progress import Progress, BarColumn, DownloadColumn, TextColumn, TimeRemainingColumn

from loom.config import get_settings


def download_gguf_model(url: str, target_filename: str, expected_sha256: str = "") -> bool:
    """Downloads model weights with Range resumption and SHA-256 verification."""
    settings = get_settings()
    models_dir = settings.paths.models_dir
    models_dir.mkdir(parents=True, exist_ok=True)
    target_path = models_dir / target_filename
    temp_path = models_dir / f"{target_filename}.part"

    resume_header = {}
    downloaded_bytes = 0
    if temp_path.exists():
        downloaded_bytes = temp_path.stat().st_size
        resume_header = {"Range": f"bytes={downloaded_bytes}-"}
        print(f"[*] Resuming download from byte offset {downloaded_bytes:,}...")

    with httpx.Client(follow_redirects=True, timeout=120.0) as client:
        with client.stream("GET", url, headers=resume_header) as response:
            if response.status_code not in (200, 206):
                print(f"[-] Download failed with HTTP {response.status_code}")
                return False

            total_bytes = int(response.headers.get("content-length", 0)) + downloaded_bytes

            mode = "ab" if downloaded_bytes > 0 else "wb"
            sha256_hasher = hashlib.sha256()

            with open(temp_path, mode) as f:
                with Progress(
                    TextColumn("[bold magenta]{task.description}"),
                    BarColumn(complete_style="magenta", finished_style="green"),
                    DownloadColumn(),
                    TimeRemainingColumn(),
                ) as progress:
                    task = progress.add_task(f"Downloading {target_filename}", total=total_bytes, completed=downloaded_bytes)

                    for chunk in response.iter_bytes(chunk_size=1024 * 1024):
                        if not chunk:
                            continue
                        f.write(chunk)
                        sha256_hasher.update(chunk)
                        progress.update(task, advance=len(chunk))

    # Rename on success
    if temp_path.exists():
        temp_path.rename(target_path)
        print(f"[+] Download complete: {target_path}")

    # Verify SHA-256 if provided
    if expected_sha256:
        print("[*] Verifying SHA-256 checksum...")
        file_hash = hashlib.sha256()
        with open(target_path, "rb") as f:
            while chunk := f.read(1024 * 1024):
                file_hash.update(chunk)
        calculated = file_hash.hexdigest()
        if calculated.lower() != expected_sha256.lower():
            print(f"[-] SHA-256 verification mismatch! Expected {expected_sha256}, got {calculated}")
            return False
        print("[+] SHA-256 verification passed!")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Loom Fabric Resumable Model Downloader")
    parser.add_argument("--url", required=True, help="Hugging Face or direct GGUF download URL")
    parser.add_argument("--filename", required=True, help="Target filename in ~/.loom/models")
    parser.add_argument("--sha256", default="", help="Expected SHA-256 checksum")
    args = parser.parse_args()

    success = download_gguf_model(args.url, args.filename, args.sha256)
    sys.exit(0 if success else 1)
