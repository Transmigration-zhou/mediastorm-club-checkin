# 影视飓风 Club 小程序自动签到脚本 — 设计文档

**日期：** 2026-05-25  
**状态：** 已批准

---

## 背景

影视飓风 Club 微信小程序每日签到可获得积分。本脚本通过抓包获得的 API 接口，在 GitHub Actions 上定时自动完成签到，并在失败时通过 Actions 邮件通知。

---

## 项目结构

```
mediastorm-club-checkin/
├── checkin.py                  # 签到脚本
├── requirements.txt            # 依赖：requests
└── .github/
    └── workflows/
        └── checkin.yml         # 定时触发 workflow
```

---

## API 信息

### 签到接口

- **方法：** GET  
- **URL：** `https://h5.youzan.com/wscump/checkin/checkinV2.json`  
- **Query 参数：**

| 参数 | 值 | 来源 |
|------|----|------|
| `checkinId` | `6287727` | 固定 |
| `app_id` | `wx92782ef90ebc836d` | 固定 |
| `kdt_id` | `149536603` | 固定 |
| `access_token` | `<动态>` | GitHub Secret |

- **请求头：**

| Header | 值 |
|--------|----|
| `User-Agent` | 微信小程序 UA（固定字符串） |
| `xweb_xhr` | `1` |
| `Content-Type` | `application/json` |
| `Referer` | `https://servicewechat.com/wx92782ef90ebc836d/17/page-frame.html` |
| `Extra-Data` | JSON，含动态 `ftime`（毫秒时间戳）、随机 `uuid`、固定其余字段 |

- **`Extra-Data` 结构：**

```json
{
  "is_weapp": 1,
  "sid": "YZ1508487656046837760YZrXb0kdCs",
  "version": "2.226.7.101",
  "client": "weapp",
  "bizEnv": "wsc",
  "uuid": "<随机字符串+时间戳>",
  "ftime": "<当前毫秒时间戳>"
}
```

### 成功响应示例

```json
{
  "msg": "ok",
  "data": {
    "success": true,
    "times": 1,
    "list": [
      {
        "isSuccess": true,
        "type": "credit",
        "infos": { "title": "10积分" }
      }
    ]
  },
  "code": 0
}
```

---

## 核心逻辑（checkin.py）

```
1. 从环境变量读取 ACCESS_TOKEN
2. 构造请求头：
   - ftime = 当前毫秒时间戳
   - uuid = 随机字母数字字符串 + ftime
   - Extra-Data = JSON 序列化上述字段
3. GET 请求 checkinV2.json
4. 判断响应：
   - code == 0 且 data.success == true → 打印奖励信息 → exit 0
   - 其他情况（含 token 失效）→ 打印错误信息 → exit 1
```

> **后续优化：** 当遇到"今日已签到"的响应时，根据实际 code/msg 值将其映射为 exit 0。

---

## GitHub Actions Workflow（checkin.yml）

- **触发：** 每天 UTC 01:00（北京时间 09:00）cron 定时
- **步骤：** checkout → setup Python 3.x → pip install requests → python checkin.py
- **失败通知：** exit 1 时 Actions 标记失败，GitHub 自动发邮件给仓库所有者

---

## Secrets 配置

在仓库 **Settings → Secrets and variables → Actions** 中添加：

| Secret 名 | 说明 |
|-----------|------|
| `ACCESS_TOKEN` | 从微信小程序抓包获取的 access_token |

---

## Token 过期处理

脚本无自动刷新 token 的能力。Token 失效时脚本 exit 1，GitHub 发邮件通知，用户重新抓包并更新 Secret 即可。

---

## 不在范围内

- 自动登录 / token 刷新
- 多账号支持
- 重试机制
