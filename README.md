# Knowledge Base Bot

Telegram 知识字典 Bot，部署在 Vercel

## 部署

1. 推送到 GitHub
2. Vercel 导入部署
3. 设置 Webhook

## 本地测试

```bash
python3 -m pip install -r requirements.txt
python3 api/index.py
```

## 更新数据

在 Gist 更新 concepts.json，Bot 自动同步
