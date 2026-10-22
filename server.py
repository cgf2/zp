#!/usr/bin/env python3
# ========== 陈氏家族网站 + 论坛后端 ==========
# 零依赖，纯 Python 3 内置模块
# 启动: python server.py
# 所有设备访问同一个 IP:端口就能同步论坛

import http.server
import json
import os
import sys
import socket
import urllib.parse
import threading
from socketserver import ThreadingMixIn

PORT = int(os.environ.get('PORT', 3000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'forum_posts_db.json')
TXT_FILE = os.path.join(BASE_DIR, 'forum_posts.txt')

MIME = {
    '.html': 'text/html; charset=utf-8',
    '.css':  'text/css; charset=utf-8',
    '.js':   'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.txt':  'text/plain; charset=utf-8',
    '.png':  'image/png',
    '.jpg':  'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif':  'image/gif',
    '.svg':  'image/svg+xml',
    '.ico':  'image/x-icon',
    '.woff': 'font/woff',
    '.woff2':'font/woff2',
}

def ensure_db():
    if not os.path.exists(DB_FILE):
        posts = []
        if os.path.exists(TXT_FILE):
            with open(TXT_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    parts = line.split('||')
                    if len(parts) >= 3:
                        posts.append({
                            'id': parts[0],
                            'username': parts[1],
                            'time': parts[2],
                            'text': '||'.join(parts[3:]) if len(parts) > 3 else ''
                        })
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)

def read_posts():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print('[read_posts error]', e, file=sys.stderr)
        return []

def write_posts(posts):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

class ThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f'[{self.address_string()}] {fmt % args}', flush=True)

    def log_error(self, fmt, *args):
        print(f'[ERROR] {fmt % args}', file=sys.stderr, flush=True)

    def send_json(self, status, obj):
        try:
            body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            print('[send_json error]', e, file=sys.stderr, flush=True)

    def do_OPTIONS(self):
        try:
            self.send_response(204)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
        except: pass

    def safe_path_check(self, raw_path):
        """返回 (full_path, None) 或 (None, 错误信息)"""
        try:
            if raw_path == '/': raw_path = '/index.html'
            # 用 relpath 防止路径穿越
            raw_path = raw_path.replace('\\', '/')
            safe = os.path.relpath(os.path.join(BASE_DIR, raw_path.lstrip('/')), BASE_DIR)
            if safe.startswith('..'):
                return None, 'Forbidden'
            full = os.path.abspath(os.path.join(BASE_DIR, safe))
            if not full.startswith(BASE_DIR):
                return None, 'Forbidden'
            return full, None
        except Exception as e:
            return None, str(e)

    def do_GET(self):
        try:
            path = urllib.parse.urlparse(self.path).path
            # API
            if path == '/api/posts':
                return self.send_json(200, read_posts())

            # 静态文件
            full, err = self.safe_path_check(path)
            if err:
                return self.send_json(403, {'error': err})
            if os.path.isdir(full):
                full = os.path.join(full, 'index.html')
            if not os.path.isfile(full):
                return self.send_json(404, {'error': 'Not found: ' + path})

            ext = os.path.splitext(full)[1].lower()
            ctype = MIME.get(ext, 'application/octet-stream')
            with open(full, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            print(f'[GET error] {e}', file=sys.stderr, flush=True)
            try:
                self.send_json(500, {'error': str(e)})
            except: pass

    def do_POST(self):
        try:
            path = urllib.parse.urlparse(self.path).path
            if path == '/api/posts':
                length = int(self.headers.get('Content-Length', 0) or 0)
                raw = self.rfile.read(length).decode('utf-8') if length > 0 else ''
                data = json.loads(raw) if raw else {}
                if not data.get('username') or not data.get('text'):
                    return self.send_json(400, {'error': '缺少字段'})
                posts = read_posts()
                import time, datetime
                post = {
                    'id': data.get('id', str(time.time()).replace('.', '')),
                    'username': str(data['username'])[:20],
                    'text': str(data['text'])[:1000],
                    'time': data.get('time', datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                }
                posts.append(post)
                write_posts(posts)
                return self.send_json(200, post)
            self.send_json(404, {'error': 'Not found'})
        except Exception as e:
            print(f'[POST error] {e}', file=sys.stderr, flush=True)
            try:
                self.send_json(500, {'error': str(e)})
            except: pass

if __name__ == '__main__':
    ensure_db()
    server = ThreadedHTTPServer(('0.0.0.0', PORT), Handler)
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = '127.0.0.1'

    print('=' * 50, flush=True)
    print('  陈氏家族网站 + 论坛后端 已启动', flush=True)
    print('=' * 50, flush=True)
    print(f'本机访问:  http://localhost:{PORT}', flush=True)
    print(f'局域网访问: http://{local_ip}:{PORT}', flush=True)
    print('=' * 50, flush=True)
    print('论坛 API:', flush=True)
    print(f'  GET  /api/posts   获取所有帖子', flush=True)
    print(f'  POST /api/posts   发布新帖子  {{username, text}}', flush=True)
    print('数据文件:', DB_FILE, flush=True)
    print('=' * 50, flush=True)
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n已停止', flush=True)
        server.server_close()
