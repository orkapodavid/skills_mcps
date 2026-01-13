#!/usr/bin/env python3
import os
from skill import WindowsShareClient


def main():
    # Ensure env vars are set or edit below
    # WSK_DOMAIN (optional), WSK_USERNAME, WSK_PASSWORD, WSK_SERVER, WSK_SHARE, WSK_BASE_PATH(optional)
    client = WindowsShareClient.from_env()

    # Demo paths
    rel_dir = "agent_demo"
    rel_path = f"{rel_dir}/hello.txt"

    # Write
    client.makedirs(rel_dir)
    client.write_text(rel_path, "Hello from WindowsShareClient!\n")

    # Read
    content = client.read_text(rel_path)
    print("Read back:")
    print(content)

    # List
    print("Directory listing:", client.list_dir(rel_dir))


if __name__ == "__main__":
    main()
