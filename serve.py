"""Run:  python3 serve.py   then open  http://localhost:8765/sf-work-match.html
Serves this folder and forwards /mistral/... to api.mistral.ai so the browser doesn't block the call."""
import http.server, socketserver, urllib.request, urllib.error, ssl, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
try:
    import certifi; CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    CTX = ssl.create_default_context()

class H(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if not self.path.startswith('/mistral/'):
            self.send_error(404); return
        body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        req = urllib.request.Request('https://api.mistral.ai' + self.path[len('/mistral'):], data=body, method='POST',
              headers={'Content-Type': 'application/json', 'Authorization': self.headers.get('Authorization', '')})
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
                code, data = r.status, r.read()
        except urllib.error.HTTPError as e:
            code, data = e.code, e.read()
        except Exception as e:
            code, data = 502, ('{"error":"proxy: %s"}' % e).encode()
        self.send_response(code); self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(data)
    def log_message(self, fmt, *a):
        print(fmt % a)

PORT = 8765
socketserver.TCPServer.allow_reuse_address = True
pages = [f for f in os.listdir('.') if f.endswith('.html')]
print('HTML files in this folder:', pages or 'NONE - put sf-work-match.html next to serve.py')
with socketserver.TCPServer(('127.0.0.1', PORT), H) as s:
    print('Open http://localhost:%d/sf-work-match.html' % PORT + '   (Ctrl+C to stop)')
    s.serve_forever()
