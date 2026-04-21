#!/usr/bin/env python3
"""
Vercel Serverless Bot (Webhook方式)
"""
import json
import os
import requests
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8707663876:AAGxHF7iZNizM2eFBam4dNct10R2kRdJ7VA")
GIST_URL = "https://gist.githubusercontent.com/JK-Solution/419c641952ac616340dc5fc9fc69ed3b/raw/4baaf89b876df36abd5b68a26de7dbdab3cf49b6/gistfile1.txt"

_concepts_cache = None


def fetch_concepts():
    """从Gist拉取数据"""
    global _concepts_cache
    if _concepts_cache:
        return _concepts_cache
    try:
        resp = requests.get(GIST_URL, timeout=10)
        resp.raise_for_status()
        _concepts_cache = resp.json()
        return _concepts_cache
    except Exception as e:
        print(f"拉取失败: {e}")
        return None


def search_concept(keyword: str, data: dict) -> list:
    """搜索概念"""
    keyword = keyword.lower()
    results = []
    for c in data.get("concepts", []):
        if keyword in c["名称"].lower():
            results.append(c)
        elif any(keyword in k.lower() for k in c["关键词"]):
            results.append(c)
        elif keyword in c["描述"].lower():
            results.append(c)
    return results


def format_concept(c: dict) -> str:
    """格式化输出"""
    return f"""【{c['名称']}】

{c['描述']}

详细: {c.get('详细说明', '暂无')}

Tags: {', '.join(c['Tags'])}
关联: {', '.join(c['关联概念']) if c.get('关联概念') else '无'}
场景: {c['适用场景']}"""


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理消息"""
    text = update.message.text.strip()
    
    data = fetch_concepts()
    if not data:
        await update.message.reply_text("❌ 获取数据失败")
        return

    # 命令处理
    if text == "/all":
        concepts = data.get("concepts", [])
        msg = f"📚 共 {len(concepts)} 个概念:\n\n"
        for c in concepts:
            msg += f"• {c['名称']}\n"
        await update.message.reply_text(msg)
        return

    # 搜索
    results = search_concept(text, data)
    if not results:
        await update.message.reply_text(f"未找到: {text}\n\n试试: PE/均线/趋势/止损/仓位\n发送 /all 查看全部")
        return

    for c in results[:3]:
        await update.message.reply_text(format_concept(c))


async def handler(event, context):
    """Vercel 入口"""
    try:
        update = Update.de_json(json.loads(event["body"]), Application.bot)
        if not update.message:
            return {"statusCode": 200}
        
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        await application.process_update(update)
        return {"statusCode": 200}
    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500}
