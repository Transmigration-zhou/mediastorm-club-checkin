#!/usr/bin/env python3
"""从抓包内容一键更新签到凭证（本地 .env + GitHub Secrets）。

用法：
    python update_token.py
    然后粘贴抓包的 URL 和 Extra-Data 行，读到 token 和 sid 后自动结束。
"""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def parse_credentials(text: str) -> tuple[str, str]:
    """从抓包文本中提取 access_token 和 sid。"""
    token_match = re.search(r"access_token=([0-9a-fA-F]+)", text)
    sid_match = re.search(r'"sid"\s*:\s*"([^"]+)"', text)
    if not token_match or not sid_match:
        raise ValueError("未能从输入中提取 access_token 或 sid")
    return token_match.group(1), sid_match.group(1)


def write_env(token: str, sid: str, path: str = str(ROOT / ".env")) -> None:
    with open(path, "w") as f:
        f.write(f"ACCESS_TOKEN={token}\n")
        f.write(f"SESSION_ID={sid}\n")


def get_repo() -> str:
    """从 origin 远程地址解析 OWNER/REPO，确保 Fork 用户操作的是自己的仓库。"""
    url = subprocess.run(
        ["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True
    ).stdout.strip()
    match = re.search(r"github\.com[:/](.+?/.+?)(?:\.git)?/?$", url)
    if not match:
        raise ValueError(f"无法从 origin 地址解析仓库：{url}")
    return match.group(1)


def update_secrets(token: str, sid: str, repo: str) -> None:
    # 通过 stdin 传值，避免凭证出现在进程参数里
    for name, value in (("ACCESS_TOKEN", token), ("SESSION_ID", sid)):
        subprocess.run(["gh", "secret", "set", name, "-R", repo], input=value, text=True, check=True)


def verify(token: str, sid: str) -> bool:
    """用新凭证跑一次签到，环境变量优先于 .env，所以不必先写文件。"""
    env = {**os.environ, "ACCESS_TOKEN": token, "SESSION_ID": sid}
    return subprocess.run([sys.executable, str(ROOT / "checkin.py")], env=env).returncode == 0


def read_capture() -> str:
    """逐行读取抓包内容，凑齐 access_token 和 sid 后自动结束（无需结束键）。"""
    print("粘贴抓包内容（含 access_token 的 URL 和带 sid 的 Extra-Data 行）：")
    lines: list[str] = []
    while True:
        try:
            lines.append(input())
        except EOFError:
            break
        try:
            parse_credentials("\n".join(lines))
            break
        except ValueError:
            continue
    return "\n".join(lines)


def main() -> None:
    text = read_capture()
    try:
        token, sid = parse_credentials(text)
    except ValueError as e:
        print(f"错误：{e}")
        sys.exit(1)
    print("验证签到：")
    if not verify(token, sid):
        print("错误：新凭证验证失败，未做任何更新，请检查抓包内容")
        sys.exit(1)
    try:
        repo = get_repo()
        update_secrets(token, sid, repo)
    except FileNotFoundError:
        print("错误：未找到 gh 命令，请先安装 GitHub CLI：https://cli.github.com/")
        sys.exit(1)
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"错误：更新 GitHub Secrets 失败（请确认已运行 gh auth login）：{e}")
        sys.exit(1)
    print(f"已更新 GitHub Secrets（{repo}）")
    write_env(token, sid)
    print("已更新 .env")


if __name__ == "__main__":
    main()
