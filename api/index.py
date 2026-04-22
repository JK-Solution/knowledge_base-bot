#!/usr/bin/env python3
"""
Vercel Bot - 纯 HTTP 版本
"""
import json
import requests

BOT_TOKEN = "8707663876:AAGxHF7iZNizM2eFBam4dNct10R2kRdJ7VA"
GIST_URL = "https://gist.githubusercontent.com/JK-Solution/419c641952ac616340dc5fc9fc69ed3b/raw/4baaf89b876df36abd5b68a26de7dbdab3cf49b6/gistfile1.txt"

_data = None


def get_data():
    global _data
    if _data is None:
        try:
            r = requests.get(GIST_URL, timeout=10)
            _data = r.json()
        except:
            _data = {"concepts": []}
    return _data


def search(keyword):
    keyword = keyword.lower()
    data = get_data()
    results = []
    for c in data.get("concepts", []):
        if keyword in c.get("名称", "").lower():
            results.append(c)
        elif any(keyword in k.lower() for k in c.get("关键词", [])):
            results.append(c)
    return results


def format_c(c):
    return f"""【{c.get('名称')}】

{c.get('描述')}

详细: {c.get('详细说明', '暂无')}

Tags: {', '.join(c.get('Tags', []))}
场景: {c.get('适用场景')}"""


def send(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)


def app(environ, start_response):
    try:
        print("Request received")
        length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(length).decode('utf-8')
        print(f"Body: {body[:200]}")
        data = json.loads(body)
        
        msg = data.get("message", {})
        print(f"Message: {msg}")
        if not msg:
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [b'ok']
        
        text = msg.get("text", "").strip()
        chat_id = msg["chat"]["id"]
        
        if not text:
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [b'ok']
        
        concepts = get_data().get("concepts", [])
        
        if text == "/all":
            result = f"📚 共 {len(concepts)} 个概念:\n\n"
            for c in concepts:
                result += f"• {c.get('名称')}\n"
            send(chat_id, result)
        else:
            results = search(text)
            if results:
                for c in results[:3]:
                    send(chat_id, format_c(c))
            else:
                send(chat_id, f"未找到: {text}\n\n试试: PE/均线/趋势/止损/仓位\n发送 /all 查看全部")
        
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b'ok']
    except Exception as e:
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b'ok']
