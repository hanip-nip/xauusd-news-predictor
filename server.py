"""
Server lokal opsional untuk XAUUSD News Predictor.

Fungsi:
  1. Menyajikan index.html di http://localhost:8787
  2. Endpoint /proxy?url=...  -> CORS proxy pribadi (lebih stabil dari proxy publik)

Jalankan:  python server.py
Hanya pakai library standar Python. Proxy dibatasi ke domain data yang dipakai dashboard.
"""
import http.server
import socketserver
import urllib.parse
import urllib.request
import os
import time

# Cache sederhana: url -> (waktu, body, content-type). ForexFactory membatasi request (429),
# jadi kalender di-cache 15 menit, lainnya 30 detik. Jika sumber error, sajikan cache lama.
CACHE = {}
TTL = {"nfs.faireconomy.media": 900}

PORT = 8787
ROOT = os.path.dirname(os.path.abspath(__file__))

# Domain yang boleh diproxy (whitelist supaya tidak jadi open proxy)
ALLOWED = (
    "nfs.faireconomy.media",
    "query1.finance.yahoo.com",
    "query2.finance.yahoo.com",
    "api.gold-api.com",
    "api.bls.gov",
    "home.treasury.gov",
    "www.investing.com",
)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/proxy":
            return super().do_GET()
        target = urllib.parse.parse_qs(parsed.query).get("url", [""])[0]
        host = urllib.parse.urlparse(target).hostname or ""
        if not any(host == d for d in ALLOWED):
            self.send_error(403, "Domain tidak diizinkan")
            return
        hit = CACHE.get(target)
        if hit and time.time() - hit[0] < TTL.get(host, 30):
            return self._send(hit[1], hit[2])
        try:
            req = urllib.request.Request(target, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36",
                "Accept": "application/json,text/csv,*/*",
            })
            with urllib.request.urlopen(req, timeout=20) as r:
                body = r.read()
                ctype = r.headers.get("Content-Type", "application/octet-stream")
            CACHE[target] = (time.time(), body, ctype)
            self._send(body, ctype)
        except Exception as e:
            if hit:  # sumber error -> pakai cache lama
                return self._send(hit[1], hit[2])
            self.send_error(502, f"Gagal fetch: {e}")  # dashboard akan fallback

    def _send(self, body, ctype):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # senyap


if __name__ == "__main__":
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"XAUUSD News Predictor -> http://localhost:{PORT}")
        httpd.serve_forever()
