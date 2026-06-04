import json
import os
from http.server import BaseHTTPRequestHandler
import requests

TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    TOKEN = "8411060036:AAHmND0hwezF9r-GOjCuw6MEMyoIzKup6XE"   # <-- вставьте реальный токен

URL = f"https://api.telegram.org/bot{TOKEN}"

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '')
            if text == '/start':
                requests.post(f"{URL}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": "Привет! Я работаю на Vercel."
                })
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("ok".encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("Бот работает.".encode("utf-8"))

# Вот эта строка решит проблему:
handler = Handler
