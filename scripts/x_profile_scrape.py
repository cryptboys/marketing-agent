import json, re, html, sys, pathlib
from urllib.parse import quote
import requests

COOKIE_PATH = pathlib.Path('secrets/twitter_cookies.json')
OUT_DIR = pathlib.Path('vault/research/copycat/samples')
USERS = ['NenkMonica', 'LambeSahamjja']

BEARER='AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejfCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'

def cookies():
    return {c['name']: c['value'] for c in json.loads(COOKIE_PATH.read_text(encoding='utf-8'))}

def sess():
    ck=cookies()
    s=requests.Session(); s.cookies.update(ck)
    s.headers.update({
        'authorization': 'Bearer '+BEARER,
        'x-csrf-token': ck.get('ct0',''),
        'x-twitter-auth-type': 'OAuth2Session',
        'x-twitter-active-user': 'yes',
        'x-twitter-client-language': 'en',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
        'accept':'*/*',
        'referer':'https://x.com/'
    })
    return s

def extract_full_texts(text):
    vals=[]
    # X SSR Relay style: full_text:"..."
    for m in re.finditer(r'full_text:"((?:\\.|[^"\\])*)"', text):
        raw=m.group(1)
        try: raw=bytes(raw,'utf-8').decode('unicode_escape')
        except Exception: pass
        raw=html.unescape(raw)
        if raw and raw not in vals and len(raw)>10:
            vals.append(raw)
    return vals

def fetch_profile(user):
    s=sess()
    r=s.get(f'https://x.com/{user}', timeout=25)
    print(user, 'status', r.status_code, 'bytes', len(r.text))
    vals=extract_full_texts(r.text)
    return vals[:80]

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_data={}
    for u in USERS:
        texts=fetch_profile(u)
        all_data[u]=texts
        (OUT_DIR/f'{u}.json').write_text(json.dumps(texts, ensure_ascii=False, indent=2), encoding='utf-8')
        print(u, 'tweets', len(texts))
        for i,t in enumerate(texts[:5],1): print(f'{i}. {t[:180].replace(chr(10)," ")}')
    (OUT_DIR/'all.json').write_text(json.dumps(all_data, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__=='__main__': main()
