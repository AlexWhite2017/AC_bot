import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Просто читаем тело и логируем (появится в логах)
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        print("POST body:", body.decode())

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"bot")
