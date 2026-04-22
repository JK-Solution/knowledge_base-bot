#!/usr/bin/env python3
"""
Vercel Bot - 简化稳定版
"""
import json
import requests

BOT_TOKEN = "8707663876:AAGxHF7iZNizM2eFBam4dNct10R2kRdJ7VA"
GIST_URL = "https://gist.githubusercontent.com/JK-Solution/419c641952ac616340dc5fc9fc69ed3b/raw/4baaf89b876df36abd5b68a26de7dbdab3cf49b6/gistfile1.txt"

_concepts = None


def get_concepts():
    global _concepts
    if _concepts is None:
        try:
            r = requests.get(GIST_URL, timeout=15)
            if r.status_code == 200:
                data = r.json()
                _concepts = data.get("concepts", [])
            else:
                _concepts = []
        except Exception as e:
            print(f"Fetch error: {e}")
            _concepts = []
    return _concepts


def search(keyword):
    keyword = keyword.lower()
    results = []
    for c in get_concepts():
        name = c.get("名称", "").lower()
        kws = [k.lower() for k in c.get("关键词", [])]
        if keyword in name or keyword in kws:
            results.append(c)
    return results


def format_c(c):
    tags = ", ".join(c.get("Tags", []))
   关联 = ", ".join(c.get("关联概念", []))
    wiki = c.get("Wiki", "")
    
    msg = f"""【{c.get('名称')}】

{c.get('描述')}

场景: {c.get('适用场景')}"""
    
    if 关联:
        msg += f"\n关联: {关联}"
    if wiki:
        msg += f"\nWiki: {wiki}"
    
    return msg


def send(chat_id, text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10
        )
    except:
        pass


def app(environ, start_response):
    try:
        length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(length).decode('utf-8')
        
        if not body:
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [b'ok']
        
        try:
            data = json.loads(body)
        except:
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [b'ok']

        msg = data.get("message", {})
        if not msg:
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [b'ok']

        text = msg.get("text", "").strip()
        chat_id = msg["chat"]["id"]

        if not text:
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [b'ok']

        concepts = get_concepts()

        if text == "/all":
            result = f"📚 共 {len(concepts)} 个概念:\n"
            for c in concepts:
                result += f"• {c.get('名称')}\n"
            send(chat_id, result)
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [b'ok']

        results = search(text)
        if results:
            for c in results[:2]:
                send(chat_id, format_c(c))
        else:
            send(chat_id, f"未找到: {text}\n试试: PE/均线/趋势/止损\n发送 /all")

        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b'ok']
    except Exception as e:
        print(f"Error: {e}")
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b'ok']