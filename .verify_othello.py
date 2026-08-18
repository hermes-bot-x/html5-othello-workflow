#!/usr/bin/env python3
"""Verify HTML5 Othello workflow build."""
from __future__ import annotations
import http.server, socketserver, subprocess, sys, threading, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ok = fail = 0

def passed(m):
    global ok; ok += 1; print('PASS', m)
def failed(m):
    global fail; fail += 1; print('FAIL', m)

def main():
    html = (ROOT/'index.html').read_text()
    if 'type="module"' in html and 'js/main.js' in html: passed('html module')
    else: failed('html')
    if 'cdn.' not in html.lower() and 'src="http' not in html.lower(): passed('no external scripts')
    else: failed('external')
    if (ROOT/'css/style.css').stat().st_size > 400: passed('css')
    else: failed('css')
    for name in ['board.js','ai.js','ui.js','main.js']:
        p = ROOT/'js'/name
        r = subprocess.run(['node','--check',str(p)], capture_output=True, text=True)
        passed(f'check {name}') if r.returncode==0 else failed(f'syntax {name}')
    logic = r'''
import { createInitialBoard, legalMoves, applyMove, BLACK, countDiscs } from './js/board.js';
const b=createInitialBoard();
const m=legalMoves(b,BLACK);
if(m.length!==4) { console.error(m); process.exit(1); }
const keys=new Set(m.map(([r,c])=>r+','+c));
for (const k of ['2,3','3,2','4,5','5,4']) if(!keys.has(k)) { console.error('missing',k); process.exit(1); }
const res=applyMove(b,2,3,BLACK);
if(!res||res.flips.length!==1) process.exit(1);
const {black,white}=countDiscs(res.board);
if(black!==4||white!==1) process.exit(1);
if(applyMove(b,0,0,BLACK)!==null) process.exit(1);
console.log('LOGIC_OK');
'''
    r = subprocess.run(['node','--input-type=module','-e',logic], cwd=str(ROOT), capture_output=True, text=True)
    passed('rules') if r.returncode==0 and 'LOGIC_OK' in r.stdout else failed(f'rules {r.stderr}')

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self,*a,**k): super().__init__(*a, directory=str(ROOT), **k)
        def log_message(self,*a): pass
    with socketserver.TCPServer(('127.0.0.1',0), H) as httpd:
        port=httpd.server_address[1]
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        base=f'http://127.0.0.1:{port}'
        for path, needle in [('/', 'OTHELLO'), ('/js/board.js','legalMoves'), ('/css/style.css','felt')]:
            try:
                with urllib.request.urlopen(base+path, timeout=5) as resp:
                    body=resp.read().decode('utf-8','ignore')
                    passed(f'http {path}') if resp.status==200 and needle in body else failed(f'http {path}')
            except Exception as e:
                failed(f'http {path} {e}')
        httpd.shutdown()
    print()
    print(f'VERIFY_OK — {ok} checks' if not fail else f'VERIFY_FAIL pass={ok} fail={fail}')
    return 0 if not fail else 1

if __name__ == '__main__':
    sys.exit(main())
