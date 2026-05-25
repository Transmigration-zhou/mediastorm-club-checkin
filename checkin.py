import json
import random
import string
import sys
import time

import requests

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
    resp = requests.get(CHECKIN_URL, params=params, headers=build_headers(sid), timeout=30)
    resp.raise_for_status()
    body = resp.json()
    if body.get("code") != 0 or not body.get("data", {}).get("success"):
        print(f"签到失败: {body}")
        sys.exit(1)
    for award in body["data"].get("list", []):
        print(f"签到成功！获得: {award.get('infos', {}).get('title', '奖励')}")
