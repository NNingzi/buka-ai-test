# buka-ai-test

基于 Python、pytest 和 Playwright 的 Buka Cloud Web 自动化测试项目。
当前仅实现第一条无破坏性用例：管理员正常登录。

## 本地准备

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
Copy-Item .env.example .env
```

在本地 `.env` 中填写真实的 `ADMIN_EMAIL` 和 `ADMIN_PASSWORD`。`.env` 已被
`.gitignore` 排除，不要把真实凭据写入测试代码或 `.env.example`。

## 运行

```powershell
pytest
```

默认无头运行。需要观察浏览器时，在 `.env` 中设置 `HEADLESS=false`。

失败截图保存到 `artifacts/screenshots/`，失败 Trace 保存到
`artifacts/traces/`，HTML 报告保存为 `artifacts/report.html`。Trace 可通过以下命令查看：

```powershell
python -m playwright show-trace artifacts/traces/<trace-file>.zip
```

## 后续范围

后续再逐步增加会话保持、仪表盘、11 个导航入口、跨页面数据一致性、订单统计和
订阅价格计算测试。本阶段不执行购买、充值、修改密码、重置流量或提交工单。
