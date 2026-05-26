# 影视飓风 Club 自动签到

通过 GitHub Actions 每天自动完成影视飓风 Club 微信小程序签到，失败时邮件通知。

## 使用方式

### 1. 抓包获取凭证

在微信小程序中打开签到页面，用抓包工具（如 Stream）捕获请求，找到 `checkinV2.json` 这条请求，取出：

- **`ACCESS_TOKEN`**：URL 参数中的 `access_token` 值
- **`SESSION_ID`**：请求头 `Extra-Data` 中的 `sid` 字段值

### 2. 配置 GitHub Secrets

进入仓库 **Settings → Secrets and variables → Actions**，添加：

| Secret | 说明 |
|--------|------|
| `ACCESS_TOKEN` | 步骤 1 中获取的 access_token |
| `SESSION_ID` | 步骤 1 中获取的 sid |

### 3. 推送到 GitHub

```bash
git remote add origin <你的仓库地址>
git push -u origin master
```

推送后 Actions 自动启用，每天北京时间 09:00 执行签到。也可在 **Actions → Daily Check-in → Run workflow** 手动触发。

## 凭证过期

Token 过期时签到失败，GitHub 会自动发邮件通知。重新抓包，更新两个 Secret 即可。

## 本地运行

```bash
pip install ".[dev]"

# 创建 .env 文件
echo "ACCESS_TOKEN=your_token" > .env
echo "SESSION_ID=your_sid" >> .env

python checkin.py
```

## 开发

```bash
pip install ".[dev]"
pytest tests/
```
