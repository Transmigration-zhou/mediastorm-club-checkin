# 影视飓风 Club 自动签到

通过 GitHub Actions 每天自动完成影视飓风 Club 微信小程序签到，失败时邮件通知。

## 使用方式

### 1. Fork 本仓库

点击右上角 **Fork**，将仓库复制到自己的 GitHub 账号下。

### 2. 抓包获取凭证

在微信小程序中打开签到页面，用抓包工具（如 Stream）捕获请求，找到 `checkinV2.json` 这条请求，取出：

- **`ACCESS_TOKEN`**：URL 参数中的 `access_token` 值
- **`SESSION_ID`**：请求头 `Extra-Data` 中的 `sid` 字段值

### 3. 配置 GitHub Secrets

进入 Fork 后的仓库 **Settings → Secrets and variables → Actions**，添加：

| Secret | 说明 |
|--------|------|
| `ACCESS_TOKEN` | 步骤 2 中获取的 access_token |
| `SESSION_ID` | 步骤 2 中获取的 sid |

配置完成后 Actions 自动启用，每天北京时间 09:00 执行签到。也可在 **Actions → Daily Check-in → Run workflow** 手动触发验证。

## 凭证过期

Token 过期时签到失败，GitHub 会自动发邮件通知。重新抓包，更新两个 Secret 即可。

凭证大约每隔几天就会过期，可用一键脚本更新（需已安装并登录 [GitHub CLI](https://cli.github.com/)，且在仓库目录下运行）：

```bash
python update_token.py
```

运行后粘贴抓包的 URL（含 `access_token`）和 `Extra-Data` 行，按 Ctrl-D 结束。脚本会自动提取凭证、更新本地 `.env` 和 GitHub Secrets，并运行一次签到验证。

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
