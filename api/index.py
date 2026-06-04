import json
import os
from http.server import BaseHTTPRequestHandler
import requests

TOKEN = os.environ.get("TELEGRAM_TOKEN")  # переменная окружения
URL = f"https://api.telegram.org/bot{TOKEN}"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        data = json.loads(body)

        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '')
            if text == '/start':
                requests.post(f"{URL}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": "Бот работает на Vercel!"
                })

        self.send_response(200)
        self.end_headers()
        self.wfile.write("ok".encode())
