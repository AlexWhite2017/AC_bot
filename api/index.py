import json
import os
from http.server import BaseHTTPRequestHandler
import requests

# Токен берём из переменной окружения, если нет – вшиваем (замените на свой)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    TOKEN = 8411060036:AAHXjG8oeaP-BQSbKEpNURg_taNuyAfEy3Y   # <-- обязательно вставьте настоящий токен

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Читаем тело запроса
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)

        # Если есть сообщение – отвечаем
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '')
            if text == '/start':
                requests.post(f"{TELEGRAM_API}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": "Привет! Я работаю на Vercel."
                })

        # Всегда возвращаем 200
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("ok".encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("Бот работает.".encode("utf-8"))
