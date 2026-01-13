import os
import sys
import io
import pathlib
from typing import List, Optional, Tuple

from .config import SkillConfig


def _norm_rel(path: str) -> str:
    p = pathlib.PurePosixPath(str(path).replace("\\", "/"))
    return str(p).lstrip("/")


def _join_base(base: str, rel: str) -> str:
    rel = _norm_rel(rel)
    return f"{base}/{rel}" if base else rel


class WindowsShareClient:
    """
    A simple client that supports reading/writing files on a Windows shared drive using a service account.

    Backends:
    - Windows (nt): pywin32 + native file I/O after establishing a UNC connection
    - Cross-platform: smbprotocol.smbclient
    """

    def __init__(self, cfg: SkillConfig):
        self.cfg = cfg
        self._backend = self._detect_backend()

    @classmethod
    def from_env(cls) -> "WindowsShareClient":
        return cls(SkillConfig.from_env())

    def _detect_backend(self) -> str:
        if os.name == "nt":
            return "win32"
        return "smbprotocol"

    # Public API
    def write_text(self, relative_path: str, text: str) -> None:
        data = text.encode(self.cfg.encoding)
        self.write_bytes(relative_path, data)

    def read_text(self, relative_path: str) -> str:
        data = self.read_bytes(relative_path)
        return data.decode(self.cfg.encoding)

    def write_bytes(self, relative_path: str, data: bytes) -> None:
        if self._backend == "win32":
            self._win32_write_bytes(relative_path, data)
        else:
            self._smb_write_bytes(relative_path, data)

    def read_bytes(self, relative_path: str) -> bytes:
        if self._backend == "win32":
            return self._win32_read_bytes(relative_path)
        else:
            return self._smb_read_bytes(relative_path)

    def list_dir(self, relative_dir: str = "") -> List[str]:
        if self._backend == "win32":
            return self._win32_list_dir(relative_dir)
        else:
            return self._smb_list_dir(relative_dir)

    def exists(self, relative_path: str) -> bool:
        if self._backend == "win32":
            return self._win32_exists(relative_path)
        else:
            return self._smb_exists(relative_path)

    def makedirs(self, relative_dir: str) -> None:
        if self._backend == "win32":
            self._win32_makedirs(relative_dir)
        else:
            self._smb_makedirs(relative_dir)

    # -----------------------
    # Windows backend (pywin32)
    # -----------------------
    def _win32_unc(self, rel: str = "") -> str:
        rel = _norm_rel(rel)
        path = f"\\\\{self.cfg.server}\\{self.cfg.share}"
        if self.cfg.base_path:
            path += "\\" + self.cfg.base_path.replace("/", "\\")
        if rel:
            path += "\\" + rel.replace("/", "\\")
        return path

    def _win32_connect(self) -> None:
        import win32wnet
        import win32netcon
        unc_root = self._win32_unc()
        user = f"{self.cfg.domain}\\{self.cfg.username}" if self.cfg.domain else self.cfg.username
        try:
            # First try to cancel any stale connection (ignore errors)
            try:
                win32wnet.WNetCancelConnection2(unc_root, 0, True)
            except Exception:
                pass
            win32wnet.WNetAddConnection2(
                win32netcon.RESOURCETYPE_DISK,
                None,
                unc_root,
                None,
                user,
                self.cfg.password,
                0,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to connect to {unc_root} as {user}: {e}")

    def _win32_write_bytes(self, relative_path: str, data: bytes) -> None:
        self._win32_connect()
        full_path = self._win32_unc(relative_path)
        dir_path = os.path.dirname(full_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(data)

    def _win32_read_bytes(self, relative_path: str) -> bytes:
        self._win32_connect()
        full_path = self._win32_unc(relative_path)
        with open(full_path, "rb") as f:
            return f.read()

    def _win32_list_dir(self, relative_dir: str = "") -> List[str]:
        self._win32_connect()
        dir_path = self._win32_unc(relative_dir)
        return sorted(os.listdir(dir_path))

    def _win32_exists(self, relative_path: str) -> bool:
        self._win32_connect()
        return os.path.exists(self._win32_unc(relative_path))

    def _win32_makedirs(self, relative_dir: str) -> None:
        self._win32_connect()
        os.makedirs(self._win32_unc(relative_dir), exist_ok=True)

    # -----------------------------
    # Cross-platform (smbprotocol)
    # -----------------------------
    def _smb_register(self) -> None:
        from smbprotocol.connection import Connection
        from smbprotocol.session import Session
        from smbprotocol.tree import TreeConnect
        from smbprotocol.open import Open
        # Use high-level smbclient convenience APIs instead
        import smbclient  # type: ignore

        server = self.cfg.server
        user = f"{self.cfg.domain}\\{self.cfg.username}" if self.cfg.domain else self.cfg.username
        smbclient.register_session(server, username=user, password=self.cfg.password)

    def _smb_url(self, rel: str = "") -> str:
        rel = _join_base(self.cfg.base_path, rel)
        # smbclient uses OS-style separators; we'll normalize to '/'
        rel = rel.replace("\\", "/")
        return f"//{self.cfg.server}/{self.cfg.share}/" + rel if rel else f"//{self.cfg.server}/{self.cfg.share}"

    def _smb_write_bytes(self, relative_path: str, data: bytes) -> None:
        import smbclient  # type: ignore
        self._smb_register()
        url = self._smb_url(relative_path)
        parent = str(pathlib.PurePosixPath(url).parent)
        try:
            smbclient.makedirs(parent, exist_ok=True)
        except Exception:
            # If parent is share root, makedirs may fail; ignore
            pass
        with smbclient.open_file(url, mode="wb") as fd:
            fd.write(data)

    def _smb_read_bytes(self, relative_path: str) -> bytes:
        import smbclient  # type: ignore
        self._smb_register()
        url = self._smb_url(relative_path)
        with smbclient.open_file(url, mode="rb") as fd:
            return fd.read()

    def _smb_list_dir(self, relative_dir: str = "") -> List[str]:
        import smbclient  # type: ignore
        self._smb_register()
        url = self._smb_url(relative_dir)
        return sorted(list(smbclient.listdir(url)))

    def _smb_exists(self, relative_path: str) -> bool:
        import smbclient  # type: ignore
        self._smb_register()
        url = self._smb_url(relative_path)
        try:
            return smbclient.path.exists(url)
        except Exception:
            return False

    def _smb_makedirs(self, relative_dir: str) -> None:
        import smbclient  # type: ignore
        self._smb_register()
        url = self._smb_url(relative_dir)
        smbclient.makedirs(url, exist_ok=True)
