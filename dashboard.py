#!/usr/bin/env python3
"""Offline-capable browser UI for the existing Celeste harness. Loopback only."""
import argparse
import json
import re
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from wiki import ROOT, TOPICS, ask, chat_turn, load_config, save_record
from retrieval import build_index, search
from local_model import LocalModel, ModelError

MODEL_LOCK = threading.Lock()
ASSETS = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'),
          '/style.css': ('style.css', 'text/css'), '/pitch.svg': ('pitch.svg', 'image/svg+xml')}


def catalog():
    return json.loads((ROOT / 'research/sources.json').read_text())['sources']


def bootstrap():
    notes = []
    for relative, sid, section, related in TOPICS:
        path = ROOT / 'vault/wiki' / (relative + '.md')
        if not path.exists():
            continue
        text = path.read_text()
        body = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.S).strip()
        notes.append(dict(id=relative, title=path.stem, category=relative.split('/')[0],
                          source_id=sid, section=section, related=related, body=body,
                          reviewed='review_status: reviewed_by_assistant' in text))
    return dict(matches=json.loads((ROOT / 'data/matches.json').read_text()), notes=notes,
                sources=[{k: s[k] for k in ('id', 'title', 'publisher', 'authors', 'permanent_url', 'text_path', 'license_urls')} for s in catalog()],
                model=load_config()['model'])


def validate_query(data):
    if not isinstance(data, dict):
        raise ValueError('A JSON object is required.')
    mode = data.get('mode')
    if mode not in ('ask', 'chat', 'search'):
        raise ValueError('Choose Ask, Chat, or Search.')
    question = data.get('question')
    if not isinstance(question, str) or not question.strip() or len(question) > 4000:
        raise ValueError('Enter a question of 1–4,000 characters.')
    # History is accepted only for chat, never for standalone research or search.
    history = data.get('history', []) if mode == 'chat' else []
    if not isinstance(history, list) or len(history) > 10:
        raise ValueError('Chat accepts at most five previous exchanges.')
    clean = []
    for item in history:
        if (not isinstance(item, dict) or item.get('role') not in ('user', 'assistant')
                or not isinstance(item.get('content'), str) or len(item['content']) > 12000):
            raise ValueError('Invalid chat history.')
        clean.append({'role': item['role'], 'content': item['content']})
    return mode, question.strip(), clean


def run_query(data):
    mode, question, history = validate_query(data)
    cfg = load_config()
    if mode == 'search':
        passages = search(ROOT, question, cfg['retrieval_count'])
        answer = f'{len(passages)} original passages found. No model was called.'
        record = dict(interaction_mode='search', question=question, answer=answer,
                      passages=passages, model_called=False)
        record['evidence_path'] = save_record(record)
    else:
        if not MODEL_LOCK.acquire(blocking=False):
            raise BlockingIOError('Celeste is answering another question. Try again when it finishes.')
        try:
            if mode == 'ask':
                record = ask(question, cfg)
            else:
                answer, path = chat_turn(question, history, cfg)
                record = json.loads((ROOT / path).read_text())
                record.update(answer=answer, evidence_path=path)
        finally:
            MODEL_LOCK.release()
    metrics = record.get('model', {}).get('measurements', {})
    return dict(answer=record['answer'], passages=record.get('passages', []),
                evidence_id=record['evidence_path'].split('/')[-1].removesuffix('.json'),
                mode=mode, seconds=metrics.get('wall_seconds'),
                citation_check=record.get('citation_check'), history=history if mode == 'chat' else [])


class Handler(BaseHTTPRequestHandler):
    def send(self, code, value, mime='application/json'):
        payload = json.dumps(value, ensure_ascii=False).encode() if mime == 'application/json' else value
        self.send_response(code)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        try:
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def trusted_request(self):
        port = self.server.server_port
        allowed = {f'127.0.0.1:{port}', f'localhost:{port}'}
        if self.headers.get('Host') not in allowed:
            self.send(403, {'error': 'Use the local dashboard address.'})
            return False
        origin = self.headers.get('Origin')
        if origin and origin not in {'http://' + host for host in allowed}:
            self.send(403, {'error': 'Only same-origin requests are accepted.'})
            return False
        return True

    def do_GET(self):
        if not self.trusted_request():
            return
        path = urlsplit(self.path).path
        try:
            if path in ASSETS:
                name, mime = ASSETS[path]
                return self.send(200, (ROOT / 'web' / name).read_bytes(), mime)
            if path == '/api/bootstrap':
                return self.send(200, bootstrap())
            if path == '/api/status':
                cfg = load_config()
                try:
                    identity = LocalModel(cfg).identity()
                    return self.send(200, dict(ready=True, model=identity['model'], runtime=identity['runtime']))
                except ModelError:
                    return self.send(200, dict(ready=False, model=cfg['model'], message='Start Ollama and download the configured model. Browsing and search still work.'))
            if path.startswith('/api/source/'):
                sid = path.rsplit('/', 1)[-1]
                source = next((s for s in catalog() if s['id'] == sid), None)
                if source:
                    return self.send(200, dict(title=source['title'], text=(ROOT / source['text_path']).read_text(),
                                               url=source['permanent_url'], authors=source['authors'], licenses=source['license_urls']))
            if path.startswith('/api/evidence/'):
                rid = path.rsplit('/', 1)[-1]
                if re.fullmatch(r'\d{8}T\d{6}-(?:ask|chat|search)-[a-f0-9]{6}', rid):
                    record = ROOT / 'evidence/runs' / (rid + '.json')
                    if record.is_file():
                        # Public browser export omits local usernames from runtime vendor paths.
                        return self.send(200, re.sub(r'/Users/[^/\s"\\]+', '/Users/REDACTED', record.read_text()).encode(), 'text/plain')
            self.send(404, {'error': 'Not found.'})
        except (OSError, ValueError, KeyError) as exc:
            self.send(500, {'error': 'Unable to read local project data: ' + str(exc)})

    def do_POST(self):
        if not self.trusted_request():
            return
        if self.path != '/api/query':
            return self.send(404, {'error': 'Not found.'})
        try:
            if self.headers.get_content_type() != 'application/json':
                return self.send(415, {'error': 'Use application/json.'})
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 150000:
                return self.send(413, {'error': 'Request is too large or empty.'})
            data = json.loads(self.rfile.read(size))
            self.send(200, run_query(data))
        except BlockingIOError as exc:
            self.send(409, {'error': str(exc)})
        except (ValueError, TypeError) as exc:
            self.send(400, {'error': str(exc)})
        except (ModelError, OSError, KeyError) as exc:
            self.send(503, {'error': str(exc)})


def main():
    parser = argparse.ArgumentParser(description='Open the local Celeste dashboard; no cloud services or asset downloads.')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--open', action='store_true', help='Open the dashboard in the default browser')
    args = parser.parse_args()
    build_index(ROOT, load_config())
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Celeste 2010 → http://127.0.0.1:{server.server_port}\nKeep this terminal open. Ctrl+C stops the dashboard.', flush=True)
    if args.open:
        threading.Timer(0.4, lambda: webbrowser.open(f'http://127.0.0.1:{server.server_port}')).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
