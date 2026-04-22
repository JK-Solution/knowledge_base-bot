#!/usr/bin/env python3
"""
Vercel Bot - Wiki增强版
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
    return get_data


def fetch_wiki_summary(url):
    """从Wiki获取摘要"""
    if not url:
        return None
    try:
        # 提取Wiki标题
        if "wikipedia.org/wiki/" in url:
            title = url.split("/wiki/")[-1]
            api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
            r = requests.get(api_url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                return data.get("extract", "")[:500]  # 截取前500字
    except:
        pass
    return None


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


def format_c(c, wiki_summary=None):
    msg = f"""【{c.get('名称')}】

{c.get('描述')}

场景: {c.get('适用场景')}"""

    # 添加Wiki摘要
    if wiki_summary:
        msg += f"\n\n📖 Wiki补充:\n{wiki_summary}..."

    if c.get("关联概念"):
        msg += f"\n\n关联: {', '.join(c.get('关联概念'))}"

    return msg


def send(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)


def app(environ, start_response):
    try:
        length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(length).decode('utf-8')
        data = json.loads(body)

        msg = data.get("message", {})
        if not msg:
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [b'ok']

        text = msg.get("text", "").strip()
        chat_id = msg["chat"]["id"]

        if not text:
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [b'ok']

        data = get_data()

        # /all 命令
        if text == "/all":
            concepts = data.get("concepts", [])
            result = f"📚 共 {len(concepts)} 个概念:\n"
            for c in concepts:
                result += f"• {c.get('名称')}\n"
            send(chat_id, result)
            return [b'ok']

        # 搜索
        results = search(text)
        if results:
            for c in results[:2]:
                wiki_url = c.get("Wiki")
                wiki_summary = fetch_wiki_summary(wiki_url) if wiki_url else None
                send(chat_id, format_c(c, wiki_summary))
        else:
            send(chat_id, f"未找到: {text}\n\n试试: PE/均线/趋势/止损/仓位\n发送 /all")

        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b'ok']
    except Exception as e:
        print(f"Error: {e}")
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b'ok']