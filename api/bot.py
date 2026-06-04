import json
import os
from http.server import BaseHTTPRequestHandler
import requests

# Токен лучше потом заменить на переменную окружения, но для первого раза вставим прямо
TELEGRAM_TOKEN = "ВАШ_ТОКЕН_БОТА"
URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        update = json.loads(body)

        if 'message' in update:
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            if text == '/start':
                requests.post(f"{URL}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": "Бот работает на Vercel!"
                })

        self.send_response(200)
        self.end_headers()
        self.wfile.write("ok".encode())
