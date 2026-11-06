# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
ClothOS Multi-User Account & Security Management Engine (`loom/clothos/user_manager.py`).

Provides Ubuntu/UNIX multi-user authentication, privilege separation, and ring mapping:
1. User Management: useradd, userdel, passwd, whoami, id, su, sudo.
2. Shadow Authentication: Secure salted SHA-256 password hashing (/etc/passwd & /etc/shadow).
3. Capability Ring Assignment:
   - root (UID 0): Ring P0 (Full Kernel & Silicon Access)
   - wheel/admin (UID 1000): Ring P1/P2 (Sudoer & Hardware Management)
   - standard user (UID 1001+): Ring P3/P4 (Isolated User Sandbox)
4. Home Directory Creation: Automatic provisioning of /home/<user>/ (Desktop, Documents, Downloads).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple

from loom.clothos.fs import cloth_fs

logger = logging.getLogger("loom.clothos.users")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class UserAccount:
    username: str
    uid: int
    gid: int
    full_name: str
    home_dir: str
    shell: str
    salt: str
    password_hash: str
    groups: List[str]
    ring_level: str  # "P0", "P1", "P2", "P3", "P4"
    created_at: str


class ClothOSUserManager:
    """Manages UNIX user accounts, authentication tokens, and capability rings."""

    _instance: Optional["ClothOSUserManager"] = None

    @classmethod
    def get_instance(cls) -> "ClothOSUserManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or WORKSPACE_ROOT
        self.accounts_file = self.workspace_root / "deliverables" / "users" / "clothos_users_ledger.json"
        self.accounts_file.parent.mkdir(parents=True, exist_ok=True)
        self.users: Dict[str, UserAccount] = {}
        self.current_user: str = "clothos"
        self._load_or_init_users()

    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        salt = salt or os.urandom(8).hex()
        pwd_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
        return salt, pwd_hash

    def _load_or_init_users(self) -> None:
        """Loads persistent user accounts or provisions baseline root & clothos users."""
        if self.accounts_file.exists():
            try:
                data = json.loads(self.accounts_file.read_text(encoding="utf-8"))
                for u in data:
                    self.users[u["username"]] = UserAccount(**u)
                if "clothos" in self.users:
                    self._sync_vfs_passwd()
                    return
            except Exception as e:
                logger.debug(f"User load note: {e}")

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

        # 1. Root user (P0 Ring)
        salt_root, hash_root = self._hash_password("sovereign")
        self.users["root"] = UserAccount(
            username="root",
            uid=0,
            gid=0,
            full_name="System Administrator",
            home_dir="/root",
            shell="/bin/bash",
            salt=salt_root,
            password_hash=hash_root,
            groups=["root", "wheel", "sudo"],
            ring_level="P0",
            created_at=now,
        )

        # 2. Default Desktop User (P1/P2 Ring)
        salt_user, hash_user = self._hash_password("clothos")
        self.users["clothos"] = UserAccount(
            username="clothos",
            uid=1000,
            gid=1000,
            full_name="ClothOS Primary Operator",
            home_dir="/home/clothos",
            shell="/bin/bash",
            salt=salt_user,
            password_hash=hash_user,
            groups=["clothos", "sudo", "audio", "video", "docker"],
            ring_level="P1",
            created_at=now,
        )

        self._save_users()
        self._provision_home_dirs()
        self._sync_vfs_passwd()

    def _save_users(self) -> None:
        try:
            data = [asdict(u) for u in self.users.values()]
            self.accounts_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to persist user ledger: {e}")

    def _provision_home_dirs(self) -> None:
        """Creates user home directory structure in ClothFS."""
        for u in self.users.values():
            base = u.home_dir
            cloth_fs.mkdir(base)
            cloth_fs.mkdir(f"{base}/Desktop")
            cloth_fs.mkdir(f"{base}/Documents")
            cloth_fs.mkdir(f"{base}/Downloads")
            cloth_fs.mkdir(f"{base}/Music")
            cloth_fs.mkdir(f"{base}/Pictures")
            cloth_fs.mkdir(f"{base}/Code")

    def _sync_vfs_passwd(self) -> None:
        """Generates standard /etc/passwd and /etc/shadow files in ClothFS."""
        passwd_lines = []
        shadow_lines = []
        for u in self.users.values():
            passwd_lines.append(f"{u.username}:x:{u.uid}:{u.gid}:{u.full_name}:{u.home_dir}:{u.shell}")
            shadow_lines.append(f"{u.username}:${u.salt}${u.password_hash}:19800:0:99999:7:::")

        cloth_fs.write_file("/etc/passwd", ("\n".join(passwd_lines) + "\n").encode("utf-8"))
        cloth_fs.write_file("/etc/shadow", ("\n".join(shadow_lines) + "\n").encode("utf-8"))

    # ── Public User Operations ──────────────────────────────────────────────

    def create_user(
        self,
        username: str,
        password: str,
        full_name: str = "",
        groups: Optional[List[str]] = None,
        ring_level: str = "P3",
    ) -> Dict[str, Any]:
        """Creates a new user account with dedicated home directory and capability ring."""
        clean_user = username.strip().lower()
        if not clean_user or not clean_user.isalnum():
            return {"success": False, "error": f"Invalid username '{clean_user}'. Must be alphanumeric."}
        if clean_user in self.users:
            return {"success": False, "error": f"User '{clean_user}' already exists."}

        next_uid = max(u.uid for u in self.users.values()) + 1
        salt, pwd_hash = self._hash_password(password)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

        user_acc = UserAccount(
            username=clean_user,
            uid=next_uid,
            gid=next_uid,
            full_name=full_name or clean_user.capitalize(),
            home_dir=f"/home/{clean_user}",
            shell="/bin/bash",
            salt=salt,
            password_hash=pwd_hash,
            groups=groups or [clean_user],
            ring_level=ring_level,
            created_at=now,
        )

        self.users[clean_user] = user_acc
        self._save_users()
        self._provision_home_dirs()
        self._sync_vfs_passwd()

        logger.info(f"✔ User account created: {clean_user} (UID {next_uid}, Ring {ring_level})")
        return {"success": True, "user": asdict(user_acc)}

    def delete_user(self, username: str) -> bool:
        if username in self.users and username not in ("root", "clothos"):
            del self.users[username]
            self._save_users()
            self._sync_vfs_passwd()
            return True
        return False

    def authenticate(self, username: str, password: str) -> bool:
        """Verifies username and password against salted hash."""
        user = self.users.get(username)
        if not user:
            return False
        _, check_hash = self._hash_password(password, user.salt)
        return check_hash == user.password_hash

    def change_password(self, username: str, new_password: str) -> bool:
        user = self.users.get(username)
        if not user:
            return False
        salt, pwd_hash = self._hash_password(new_password)
        user.salt = salt
        user.password_hash = pwd_hash
        self._save_users()
        self._sync_vfs_passwd()
        return True

    def switch_user(self, username: str) -> bool:
        if username in self.users:
            self.current_user = username
            return True
        return False

    def list_users(self) -> List[Dict[str, Any]]:
        return [
            {
                "username": u.username,
                "uid": u.uid,
                "full_name": u.full_name,
                "home_dir": u.home_dir,
                "groups": u.groups,
                "ring_level": u.ring_level,
                "is_current": (u.username == self.current_user),
            }
            for u in self.users.values()
        ]


# Singleton instance
user_manager = ClothOSUserManager.get_instance()
