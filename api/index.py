#!/usr/bin/env python3
"""
Vercel Serverless Bot - 简化版
"""
import json
import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN", "8707663876:AAGxHF7iZNizM2eFBam4dNct10R2kRdJ7VA")
GIST_URL = "https://gist.githubusercontent.com/JK-Solution/419c641952ac616340dc5fc9fc69ed3b/raw/4baaf89b876df36abd5b68a26de7dbdab3cf49b6/gistfile1.txt"

_concepts_cache = None


def fetch_concepts():
    """从Gist拉取数据"""
    global _concepts_cache
    if _concepts_cache:
        return _concepts_cache
    try:
        resp = requests.get(GIST_URL, timeout=10)
        _concepts_cache = resp.json()
        return _concepts_cache
    except:
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
    return results


def format_concept(c: dict) -> str:
    """格式化输出"""
    return f"""【{c['名称']}】

{c['描述']}

详细: {c.get('详细说明', '暂无')}

Tags: {', '.join(c['Tags'])}
场景: {c['适用场景']}"""


def send_message(chat_id: int, text: str):
    """发送消息"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)


def app(event, context):
    """Vercel 入口"""
    try:
        body = json.loads(event.get("body", "{}"))
        message = body.get("message", {})
        
        if not message or not message.get("text"):
            return {"statusCode": 200}
        
        text = message["text"].strip()
        chat_id = message["chat"]["id"]
        
        data = fetch_concepts()
        if not data:
            send_message(chat_id, "❌ 获取数据失败")
            return {"statusCode": 200}

        # 命令处理
        if text == "/all":
            concepts = data.get("concepts", [])
            msg = f"📚 共 {len(concepts)} 个概念:\n\n"
            for c in concepts:
                msg += f"• {c['名称']}\n"
            send_message(chat_id, msg)
            return {"statusCode": 200}

        # 搜索
        results = search_concept(text, data)
        if not results:
            send_message(chat_id, f"未找到: {text}\n\n试试: PE/均线/趋势/止损/仓位\n发送 /all 查看全部")
            return {"statusCode": 200}

        for c in results[:3]:
            send_message(chat_id, format_concept(c))
        
        return {"statusCode": 200}
    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 200}