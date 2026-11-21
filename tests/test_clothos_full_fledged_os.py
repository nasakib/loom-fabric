# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Comprehensive Test Suite for Full-Fledged ClothOS Operating System (`tests/test_clothos_full_fledged_os.py`).

Verifies:
1. User Accounts & Multi-User Security: useradd, shadow password hashing, ring capabilities (P0-P4).
2. Package Manager & Runtimes: cloth-apt, rustc, cargo, java/JVM, python3, git, neofetch, curl, ping.
3. Live Bootable USB Flashdrive Creator: MBR 0x55AA signature, GPT header, hybrid installer baking.
4. Shell Compatibility: whoami, id, sudo, and pipeline execution.
"""

from pathlib import Path
import json
import pytest

from loom.clothos.user_manager import ClothOSUserManager, user_manager
from loom.clothos.package_manager import ClothOSPackageManager, package_manager
from loom.clothos.usb_installer import ClothOSUsbInstaller, usb_installer
from loom.clothos.posix_compat import ClothOSPosixSubsystem, clothos_posix


def test_user_manager_multi_user_security():
    # Verify baseline root and clothos users
    users = user_manager.list_users()
    user_map = {u["username"]: u for u in users}
    assert "root" in user_map
    assert "clothos" in user_map

    assert user_map["root"]["ring_level"] == "P0"
    assert user_map["clothos"]["ring_level"] == "P1"

    # Test creating new user (clean up if previously exists from prior run)
    user_manager.delete_user("alice")
    res = user_manager.create_user("alice", "alicepass123", full_name="Alice Developer", ring_level="P3")
    assert res["success"] is True
    assert user_manager.authenticate("alice", "alicepass123") is True
    assert user_manager.authenticate("alice", "wrongpass") is False

    # Password change
    assert user_manager.change_password("alice", "newsecret") is True
    assert user_manager.authenticate("alice", "newsecret") is True


def test_package_manager_and_runtimes():
    # Test searching packages
    rust_pkgs = package_manager.search_packages("rust")
    assert any(p["name"] == "rustc" for p in rust_pkgs)

    # Test executing runtimes
    rustc_res = package_manager.execute_program("rustc", ["--version"])
    assert "rustc 1.84" in rustc_res["stdout"]

    java_res = package_manager.execute_program("java", ["-version"])
    assert "openjdk version \"21.0.5\"" in java_res["stdout"]

    py_res = package_manager.execute_program("python3", ["--version"])
    assert "Python 3.14" in py_res["stdout"]

    git_res = package_manager.execute_program("git", ["--version"])
    assert "git version" in git_res["stdout"]

    neofetch_res = package_manager.execute_program("neofetch", [])
    assert "ClothOS Sovereign Linux" in neofetch_res["stdout"]
    assert "Systolic" in neofetch_res["stdout"]

    ping_res = package_manager.execute_program("ping", ["192.168.99.2"])
    assert "0% packet loss" in ping_res["stdout"]


def test_live_bootable_usb_image_baking():
    res = usb_installer.bake_live_usb_image()
    assert res["success"] is True
    assert res["mbr_valid"] is True
    assert res["gpt_valid"] is True
    assert res["size_mb"] >= 8.0

    img_path = Path(res["image_path"])
    assert img_path.exists()
    assert len(res["sha256_checksum"]) == 64


def test_posix_shell_integration_with_users_and_apt():
    res_whoami = clothos_posix.execute_shell_command("whoami")
    assert res_whoami["exit_code"] == 0
    assert "clothos" in res_whoami["stdout"]

    res_id = clothos_posix.execute_shell_command("id")
    assert "uid=1000" in res_id["stdout"]
    assert "ring=P1" in res_id["stdout"]

    res_apt_list = clothos_posix.execute_shell_command("cloth-apt list")
    assert res_apt_list["exit_code"] == 0
    assert "rustc" in res_apt_list["stdout"]

    res_apt_install = clothos_posix.execute_shell_command("cloth-apt install htop")
    assert res_apt_install["exit_code"] == 0
    assert "Successfully installed" in res_apt_install["stdout"]

    res_sudo = clothos_posix.execute_shell_command("sudo whoami")
    assert "P0 Elevation" in res_sudo["stdout"]
