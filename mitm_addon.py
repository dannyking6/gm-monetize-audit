"""Addon mitmproxy: journal de TOUT le trafic HTTP(s) pendant le jeu GameMonetize."""
import json, time
from mitmproxy import http

OUT = open('/tmp/gm_audit/traffic/requests.jsonl', 'a', buffering=1)

def _log(flow, phase):
    r = flow.request
    resp = getattr(flow, 'response', None)
    entry = {
        'ts': time.time(),
        'phase': phase,
        'method': r.method,
        'scheme': r.scheme,
        'host': r.host,
        'port': r.port,
        'path': r.path,
        'url': r.pretty_url,
    }
    h = {k.lower(): v for k, v in r.headers.items()}
    entry['req_headers'] = {
        'user-agent': h.get('user-agent'),
        'referer': h.get('referer'),
        'cookie': h.get('cookie'),
        'origin': h.get('origin'),
        'x-forwarded-for': h.get('x-forwarded-for'),
        'content-type': h.get('content-type'),
        'accept-language': h.get('accept-language'),
    }
    body = r.get_text(strict=False) if r.content else ''
    if body and len(body) < 20000 and phase in ('req', 'both') or (body and phase == 'req'):
        entry['req_body'] = body[:8000]
    if resp:
        entry['status'] = resp.status_code
        ct = resp.headers.get('content-type', '')
        entry['resp_content_type'] = ct
        entry['resp_len'] = len(resp.content or '')
        if resp.content and ('json' in ct or 'vast' in ct or 'xml' in (ct or '') or 'text' in ct or 'script' in ct) and len(resp.content) < 100000:
            try:
                entry['resp_body_snippet'] = resp.get_text(strict=False)[:6000]
            except Exception:
                pass
        # cookies reçus
        if resp.headers.get('set-cookie'):
            entry['set_cookie'] = resp.headers.get_all('set-cookie')
    OUT.write(json.dumps(entry, ensure_ascii=False) + '\n')

def request(flow):
    _log(flow, 'req')

def response(flow):
    _log(flow, 'both')
