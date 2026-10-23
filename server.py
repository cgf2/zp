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
DATA_JS = os.path.join(BASE_DIR, 'data.js')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'cgf')  # 后台密码，默认 cgf

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

# ========== data.js 读写 ==========
def read_family_data():
    """从 data.js 里解析 window.familyData"""
    try:
        with open(DATA_JS, 'r', encoding='utf-8') as f:
            src = f.read()
        # 找到 window.familyData = [...] 段
        import re
        m = re.search(r'window\.familyData\s*=\s*(\[.*?\])\s*;', src, re.DOTALL)
        if m:
            return json.loads(m.group(1))
    except Exception as e:
        print('[read_family_data error]', e, file=sys.stderr)
    return None

def write_family_data(new_data):
    """备份旧 data.js，把 window.familyData 段替换为 new_data，保留 forumPostData"""
    import re, shutil, datetime
    if not os.path.exists(DATA_JS):
        # 直接创建
        content = 'window.familyData = ' + json.dumps(new_data, ensure_ascii=False, indent=2) + ';\n'
        content += 'window.forumPostData = [];\n'
        with open(DATA_JS, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    # 备份
    bak = DATA_JS + '.bak'
    shutil.copy2(DATA_JS, bak)

    with open(DATA_JS, 'r', encoding='utf-8') as f:
        src = f.read()

    new_block = 'window.familyData = ' + json.dumps(new_data, ensure_ascii=False, indent=2) + ';'
    new_src, n = re.subn(r'window\.familyData\s*=\s*\[.*?\]\s*;', new_block, src, count=1, flags=re.DOTALL)

    if n == 0:
        # 没找到匹配，抛错
        raise Exception('data.js 里没找到 window.familyData 段，无法自动更新')

    with open(DATA_JS, 'w', encoding='utf-8') as f:
        f.write(new_src)

    # 清理过期备份（保留最近 5 份）
    try:
        baks = sorted([x for x in os.listdir(BASE_DIR) if x.startswith('data.js.bak')])
        for old in baks[:-5]:
            os.remove(os.path.join(BASE_DIR, old))
    except: pass
    return True

def validate_family_data(data):
    """校验上传的 zp.json 结构是否合法"""
    if not isinstance(data, list):
        return False, '顶层必须是数组'
    if len(data) == 0:
        return False, '数组不能为空'
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            return False, f'第 {i+1} 项不是对象'
        if 'ID' not in item:
            return False, f'第 {i+1} 项缺少 ID 字段'
        if '姓名' not in item:
            return False, f'第 {i+1} 项缺少 姓名字段'
    return True, ''

def parse_multipart(body, content_type):
    """极简 multipart/form-data 解析器，返回 dict {field_name: value_str, 'files': {field_name: {'filename': .., 'content': bytes}}}"""
    import re
    m = re.search(r'boundary=([^\s;]+)', content_type)
    if not m: return {}
    boundary = b'--' + m.group(1).encode()
    parts = body.split(boundary)
    result = {'files': {}}
    for part in parts:
        part = part.strip(b'\r\n')
        if not part or part == b'--':
            continue
        if part.endswith(b'--'):
            part = part[:-2]
        # 找 header 和 body 的分隔
        sep = part.find(b'\r\n\r\n')
        if sep < 0: continue
        headers = part[:sep].decode('utf-8', errors='replace')
        content = part[sep+4:]
        content = content.rstrip(b'\r\n')
        # 解析 Content-Disposition
        m2 = re.search(r'name="([^"]*)"', headers)
        if not m2: continue
        name = m2.group(1)
        fn = re.search(r'filename="([^"]*)"', headers)
        if fn:
            result['files'][name] = {'filename': fn.group(1), 'content': content}
        else:
            result[name] = content.decode('utf-8', errors='replace')
    return result

class ThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f'[{self.address_string()}] {fmt % args}', flush=True)

    def log_error(self, fmt, *args):
        print(f'[ERROR] {fmt % args}', file=sys.stderr, flush=True)

    def check_admin_pass(self):
        """检查管理密码，返回 True 表示通过"""
        # 方式一：header X-Admin-Pass
        h = self.headers.get('X-Admin-Pass', '')
        if h and h == ADMIN_PASS:
            return True
        # 方式二：query param ?pass=xxx
        q = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(q)
        if params.get('pass', [''])[0] == ADMIN_PASS:
            return True
        return False

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

            if path == '/api/data':
                data = read_family_data()
                if data is None:
                    return self.send_json(500, {'error': '无法读取 data.js'})
                # 返回概况（统计），不给全量，减轻传输
                import collections
                gens = collections.Counter()
                ids = set()
                for m in data:
                    if '代数' in m: gens[m['代数']] += 1
                    if 'ID' in m: ids.add(m['ID'])
                return self.send_json(200, {
                    'total': len(data),
                    'generations': dict(gens),
                    'has_ids': len(ids),
                    'names_preview': [m.get('姓名','') for m in data[:5]],
                })

            if path == '/api/backup/download':
                # 下载当前 data.js.bak（如果有）
                if not self.check_admin_pass():
                    return self.send_json(401, {'error': '需要管理密码（?pass=xxx）'})
                bak = DATA_JS + '.bak'
                if not os.path.exists(bak):
                    return self.send_json(404, {'error': '没有备份'})
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Disposition', 'attachment; filename="data.js.bak"')
                d = open(bak, 'rb').read()
                self.send_header('Content-Length', str(len(d)))
                self.end_headers()
                self.wfile.write(d)
                return

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

            if path == '/api/data':
                # 支持两种上传方式：
                # 1) multipart/form-data 文件上传  2) application/json 直接传数组
                if not self.check_admin_pass():
                    return self.send_json(401, {'error': '需要管理密码（header: X-Admin-Pass 或 ?pass=xxx）'})
                ct = self.headers.get('Content-Type', '')
                length = int(self.headers.get('Content-Length', 0) or 0)
                raw = self.rfile.read(length) if length > 0 else b''

                parsed = None
                if 'multipart/form-data' in ct:
                    mp = parse_multipart(raw, ct)
                    f = mp.get('files', {}).get('file') or mp.get('files', {}).get('data')
                    if f:
                        try:
                            parsed = json.loads(f['content'].decode('utf-8'))
                        except Exception as e:
                            return self.send_json(400, {'error': f'文件不是合法 JSON: {e}'})
                elif 'application/json' in ct or raw:
                    try:
                        parsed = json.loads(raw.decode('utf-8'))
                    except Exception as e:
                        return self.send_json(400, {'error': f'不是合法 JSON: {e}'})

                if parsed is None:
                    return self.send_json(400, {'error': '没有收到数据'})

                ok, err = validate_family_data(parsed)
                if not ok:
                    return self.send_json(400, {'error': '数据校验失败: ' + err})

                # 写入前备份
                before = len(read_family_data() or [])
                write_family_data(parsed)
                return self.send_json(200, {
                    'ok': True,
                    'before_count': before,
                    'after_count': len(parsed),
                    'message': f'已更新 data.js（{before} → {len(parsed)} 条），旧文件已备份为 data.js.bak'
                })

            if path == '/api/admin/post-delete':
                if not self.check_admin_pass():
                    return self.send_json(401, {'error': '需要管理密码（header: X-Admin-Pass 或 ?pass=xxx）'})
                length = int(self.headers.get('Content-Length', 0) or 0)
                raw = self.rfile.read(length).decode('utf-8') if length > 0 else ''
                data = json.loads(raw) if raw else {}
                post_id = data.get('id')
                if not post_id:
                    return self.send_json(400, {'error': '缺少帖子 ID'})
                posts = read_posts()
                new_posts = [p for p in posts if p.get('id') != post_id]
                write_posts(new_posts)
                return self.send_json(200, {'ok': True, 'deleted': len(posts) - len(new_posts)})

            if path == '/api/admin/post-clear':
                if not self.check_admin_pass():
                    return self.send_json(401, {'error': '需要管理密码（header: X-Admin-Pass 或 ?pass=xxx）'})
                write_posts([])
                return self.send_json(200, {'ok': True})

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
