#!/usr/bin/env python3
"""从抓包内容一键更新签到凭证（本地 .env + GitHub Secrets）。

用法：
    python update_token.py
    然后粘贴抓包的 URL 和 Extra-Data 行，按 Ctrl-D 结束。
"""
import re
import subprocess
import sys


def parse_credentials(text: str) -> tuple[str, str]:
    """从抓包文本中提取 access_token 和 sid。"""
    token_match = re.search(r"access_token=([0-9a-fA-F]+)", text)
    sid_match = re.search(r'"sid"\s*:\s*"([^"]+)"', text)
    if not token_match or not sid_match:
        raise ValueError("未能从输入中提取 access_token 或 sid")
    return token_match.group(1), sid_match.group(1)


def write_env(token: str, sid: str, path: str = ".env") -> None:
    with open(path, "w") as f:
        f.write(f"ACCESS_TOKEN={token}\n")
        f.write(f"SESSION_ID={sid}\n")


def update_secrets(token: str, sid: str) -> None:
    subprocess.run(["gh", "secret", "set", "ACCESS_TOKEN", "--body", token], check=True)
    subprocess.run(["gh", "secret", "set", "SESSION_ID", "--body", sid], check=True)


def main() -> None:
    print("粘贴抓包内容（含 access_token 的 URL 和带 sid 的 Extra-Data 行），然后按 Ctrl-D：")
    text = sys.stdin.read()
    try:
        token, sid = parse_credentials(text)
    except ValueError as e:
        print(f"错误：{e}")
        sys.exit(1)
    write_env(token, sid)
    print(f"已更新 .env（ACCESS_TOKEN={token[:8]}… SESSION_ID={sid[:12]}…）")
    update_secrets(token, sid)
    print("已更新 GitHub Secrets")
    print("验证签到：")
    subprocess.run([sys.executable, "checkin.py"])


if __name__ == "__main__":
    main()
