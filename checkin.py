import json
import os
import random
import string
import sys
import time

import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

CHECKIN_URL = "https://h5.youzan.com/wscump/checkin/checkinV2.json"
APP_ID = "wx92782ef90ebc836d"
KDT_ID = "149536603"
CHECKIN_ID = "6287727"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 "
    "MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI "
    "MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.7(0x13080712) "
    "UnifiedPCMacWechat(0xf2641702) XWEB/18788"
)

# Configure session with retry logic for transient errors
_session = requests.Session()
_retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
_session.mount("https://", HTTPAdapter(max_retries=_retry))


def build_extra_data(sid: str) -> str:
    ftime = int(time.time() * 1000)
    uuid = "".join(random.choices(string.ascii_letters, k=15)) + str(ftime)
    return json.dumps(
        {
            "is_weapp": 1,
            "sid": sid,
            "version": "2.226.7.101",
            "client": "weapp",
            "bizEnv": "wsc",
            "uuid": uuid,
            "ftime": ftime,
        },
        separators=(",", ":"),
    )


def build_headers(sid: str) -> dict:
    return {
        "User-Agent": USER_AGENT,
        "xweb_xhr": "1",
        "Content-Type": "application/json",
        "Referer": "https://servicewechat.com/wx92782ef90ebc836d/17/page-frame.html",
        "Extra-Data": build_extra_data(sid),
    }


def do_checkin(access_token: str, sid: str) -> None:
    params = {
        "checkinId": CHECKIN_ID,
        "app_id": APP_ID,
        "kdt_id": KDT_ID,
        "access_token": access_token,
    }
    resp = _session.get(CHECKIN_URL, params=params, headers=build_headers(sid), timeout=30)
    resp.raise_for_status()
    body = resp.json()
    if body.get("code") == 1000030071:
        print("今日已签到，跳过")
        return
    data = body.get("data") or {}
    if body.get("code") != 0 or not data.get("success"):
        print(f"签到失败: {body}")
        sys.exit(1)
    awards = data.get("list", [])
    if not awards:
        print("签到成功！")
    for award in awards:
        print(f"签到成功！获得: {award.get('infos', {}).get('title', '奖励')}")


def _load_env(env_file: str = "") -> None:
    if not env_file:
        env_file = os.path.join(os.path.dirname(str(__file__)), ".env")
    if not os.path.exists(env_file):
        return
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                value = value.split(" #")[0].strip()
                os.environ.setdefault(key.strip(), value)


_load_env()


def main() -> None:
    access_token = os.environ.get("ACCESS_TOKEN")
    sid = os.environ.get("SESSION_ID")
    if not access_token or not sid:
        print("错误: 缺少 ACCESS_TOKEN 或 SESSION_ID 环境变量")
        sys.exit(1)
    do_checkin(access_token, sid)


if __name__ == "__main__":
    main()
