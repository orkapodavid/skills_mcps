import os
import tempfile
from skill import WindowsShareClient, SkillConfig


def test_norm_flow(monkeypatch):
    # This is a smoke test structure; actual SMB calls require environment.
    # Validate that client can be constructed from env variables.
    monkeypatch.setenv("WSK_USERNAME", "user")
    monkeypatch.setenv("WSK_PASSWORD", "pass")
    monkeypatch.setenv("WSK_SERVER", "server")
    monkeypatch.setenv("WSK_SHARE", "share")
    c = WindowsShareClient.from_env()
    assert c.cfg.username == "user"
