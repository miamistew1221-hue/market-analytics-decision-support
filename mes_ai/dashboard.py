"""Local-only HTTP dashboard. No external packages, no trade execution."""
import argparse,json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from .core import load_candles,analyze

HTML='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MES Research AI</title><style>body{background:#101827;color:#e9eef8;font:16px system-ui;margin:0;padding:35px}main{max-width:950px;margin:auto}.panel{background:#1b2940;padding:22px;border-radius:16px;margin:18px 0}h1{font-size:34px}small{color:#9bb0d0}.warn{color:#ffd38b}pre{white-space:pre-wrap;overflow-wrap:anywhere}table{width:100%;border-collapse:collapse}td,th{padding:10px;text-align:left;border-bottom:1px solid #384862}</style></head><body><main><h1>MES Trading AI — Research Dashboard</h1><p class="warn">Educational demonstration · Not a certified 41-specialist strategy · No broker orders</p><div class="panel"><h2>Data feed</h2><p id="feed">Loading…</p></div><div class="panel"><h2>Research signals</h2><p id="count"></p><table><thead><tr><th>Timestamp</th><th>Side</th><th>Close</th><th>Detector</th></tr></thead><tbody id="rows"></tbody></table></div><small>Data: bundled synthetic sample by default. For Quantower, export completed 1-minute candles and run the read-only bridge.</small></main><script>async function refresh(){try{const d=await (await fetch('/api/status')).json();document.getElementById('feed').textContent=`${d.status} · ${d.bars||0} completed candles · Last: ${d.last_bar||'N/A'}`;document.getElementById('count').textContent=`${(d.signals||[]).length} research events`;document.getElementById('rows').replaceChildren(...(d.signals||[]).slice(-20).reverse().map(s=>{let tr=document.createElement('tr');for(let v of [s.timestamp,s.side,s.close,s.type]){let td=document.createElement('td');td.textContent=v;tr.append(td)}return tr}));}catch(e){document.getElementById('feed').textContent=String(e)}}refresh();setInterval(refresh,5000)</script></body></html>'''

def main():
    p=argparse.ArgumentParser();p.add_argument('--csv',default='sample_data/synthetic_mes_1m.csv');p.add_argument('--port',type=int,default=8765);args=p.parse_args()
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path=='/':body=HTML.encode();kind='text/html; charset=utf-8'
            elif self.path=='/api/status':
                try: body=json.dumps(analyze(load_candles(args.csv))).encode()
                except (OSError,ValueError) as e:body=json.dumps({'status':'BLOCKED','error':str(e)}).encode()
                kind='application/json'
            else:self.send_error(404);return
            self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    print(f'Dashboard: http://127.0.0.1:{args.port}')
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
if __name__=='__main__':main()
