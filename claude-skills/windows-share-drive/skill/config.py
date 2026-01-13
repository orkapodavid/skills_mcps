from dataclasses import dataclass
import os
from typing import Optional


def _getenv(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name, default)
    return v if v is None or v.strip() != "" else default


@dataclass
class SkillConfig:
    domain: Optional[str]
    username: str
    password: str
    server: str
    share: str
    base_path: str = ""
    encoding: str = "utf-8"

    @classmethod
    def from_env(cls) -> "SkillConfig":
        username = os.getenv("WSK_USERNAME")
        password = os.getenv("WSK_PASSWORD")
        server = os.getenv("WSK_SERVER")
        share = os.getenv("WSK_SHARE")
        if not all([username, password, server, share]):
            missing = [k for k, v in {
                'WSK_USERNAME': username,
                'WSK_PASSWORD': password,
                'WSK_SERVER': server,
                'WSK_SHARE': share,
            }.items() if not v]
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        return cls(
            domain=_getenv("WSK_DOMAIN"),
            username=username,
            password=password,
            server=server,
            share=share,
            base_path=_getenv("WSK_BASE_PATH", "") or "",
            encoding=_getenv("WSK_ENCODING", "utf-8") or "utf-8",
        )
