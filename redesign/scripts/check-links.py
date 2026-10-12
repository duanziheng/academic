"""Check every link on the live site and write a Markdown report.

    python3 redesign/scripts/check-links.py https://zihengduan.cn report.md

Reads the sitemap and collects every link and resource on every page, and every link in the CV PDF (/cv):
- Pages and files on the site itself must answer 200.
- DOI links are checked with doi.org's handle API, since publishers often refuse automated requests.
- GitHub repositories are checked with the GitHub API. Set GITHUB_TOKEN to raise the rate limit.
- Other links count as broken on 404 or 410, or when the host cannot be reached. Answers such as 401, 403, 429 or
  999 come from publishers and sites that block automated requests; they are listed as unverified, not as broken.

The exit status is 1 when a link is broken, so a scheduled workflow can open an issue (.github/workflows/link-check.yml).
Uses the standard library only.
"""
import concurrent.futures as cf
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from html.parser import HTMLParser

UA = 'Mozilla/5.0 (compatible; zihengduan.cn link check; +https://zihengduan.cn/)'
BLOCKING = {401, 403, 405, 406, 409, 418, 425, 429, 451, 999}


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ('href', 'src', 'data-cite'):
            v = a.get(key)
            if v and not v.startswith(('mailto:', 'tel:', 'javascript:', 'data:', '#')):
                self.found.append(v)


def pdf_links(data):
    """the link targets (/URI) in a PDF, including those in compressed object streams, where pdfTeX writes them"""
    found = set(re.findall(rb'/URI\s*\(([^)]*)\)', data))
    for m in re.finditer(rb'stream\r?\n', data):
        start = m.end()
        try:
            found.update(re.findall(rb'/URI\s*\(([^)]*)\)', zlib.decompress(data[start:data.find(b'endstream', start)])))
        except zlib.error:
            pass                                    # not a Flate stream
    return sorted(u.decode('latin-1').replace('\\(', '(').replace('\\)', ')') for u in found)


def fetch(url, method='GET', timeout=30, headers=None):
    req = urllib.request.Request(url, method=method, headers={'User-Agent': UA, 'Accept': '*/*', **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read() if method == 'GET' else b''


def status(url):
    """an HTTP status, or a short error string when the host could not be reached"""
    for attempt in range(2):
        for method in ('HEAD', 'GET'):
            try:
                return fetch(url, method)[0]
            except urllib.error.HTTPError as e:
                if method == 'HEAD' and e.code in BLOCKING | {404, 500, 501, 502, 503}:
                    continue            # some servers refuse HEAD: try GET
                return e.code
            except Exception as e:      # DNS failure, refused connection, timeout, TLS error
                err = type(e).__name__ + ': ' + str(getattr(e, 'reason', e))[:80]
                if method == 'GET':
                    break
        time.sleep(3)
    return err


def check_doi(doi):
    try:
        _, body = fetch('https://doi.org/api/handles/' + urllib.parse.quote(doi, safe='/'))
        return 'ok' if json.loads(body).get('responseCode') == 1 else 'DOI not found'
    except urllib.error.HTTPError as e:
        return 'DOI not found' if e.code == 404 else f'doi.org answered {e.code}'
    except Exception as e:
        return 'doi.org unreachable: ' + type(e).__name__


def check_github(owner, repo):
    headers = {'Accept': 'application/vnd.github+json'}
    if os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    path = f'repos/{owner}/{repo}' if repo else f'users/{owner}'
    try:
        fetch('https://api.github.com/' + path, headers=headers)
        return 'ok'
    except urllib.error.HTTPError as e:
        return 'not found on GitHub' if e.code == 404 else f'GitHub API answered {e.code}'
    except Exception as e:
        return 'GitHub API unreachable: ' + type(e).__name__


def main(base, out):
    base = base.rstrip('/')
    host = urllib.parse.urlsplit(base).netloc
    _, sm = fetch(base + '/sitemap.xml')
    pages = re.findall(r'<loc>([^<]+)</loc>', sm.decode())
    where = {}                                       # link -> pages it appears on
    for page in pages:
        _, html = fetch(page)
        p = Links(); p.feed(html.decode('utf-8', 'replace'))
        for link in p.found:
            url = urllib.parse.urljoin(page, link).split('#')[0]
            if urllib.parse.urlsplit(url).netloc == host:
                url = base + urllib.parse.urlsplit(url).path + (('?' + urllib.parse.urlsplit(url).query) if urllib.parse.urlsplit(url).query else '')
            where.setdefault(url, set()).add(urllib.parse.urlsplit(page).path)
    try:                                             # the CV's links: DOIs, labs, project pages
        _, cv = fetch(base + '/cv')
        cv_links = [u for u in pdf_links(cv) if u.startswith(('http://', 'https://'))]
        for link in cv_links:
            where.setdefault(link.split('#')[0], set()).add('the CV (/cv)')
    except Exception as e:
        cv_links = None
        print('Could not read the CV PDF:', type(e).__name__, e)

    def judge(url):
        u = urllib.parse.urlsplit(url)
        if u.scheme not in ('http', 'https'):
            return url, 'skip', ''
        if u.netloc in ('doi.org', 'dx.doi.org'):
            r = check_doi(urllib.parse.unquote(u.path.lstrip('/')))
            return url, ('ok' if r == 'ok' else 'broken' if r == 'DOI not found' else 'unverified'), r
        m = re.match(r'^/([^/]+)(?:/([^/]+))?/?$', u.path)
        if u.netloc == 'github.com' and m:
            r = check_github(m.group(1), m.group(2))
            return url, ('ok' if r == 'ok' else 'broken' if r == 'not found on GitHub' else 'unverified'), r
        s = status(url)
        if s == 200 or (isinstance(s, int) and 200 <= s < 400):
            return url, 'ok', str(s)
        if isinstance(s, int) and (s in BLOCKING or s >= 500) and u.netloc != host:
            return url, 'unverified', f'answered {s}'
        return url, 'broken', str(s)

    with cf.ThreadPoolExecutor(8) as ex:
        results = list(ex.map(judge, sorted(where)))
    broken = [r for r in results if r[1] == 'broken']
    unverified = [r for r in results if r[1] == 'unverified']
    cv_note = f' and {len(cv_links)} in the CV PDF' if cv_links else (' (the CV PDF could not be read)' if cv_links is None else '')
    lines = [f'Checked {len(results)} links on {len(pages)} pages of {base}{cv_note} ({time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}).', '']
    if broken:
        lines += [f'### Broken ({len(broken)})', '']
        lines += [f'- {url} — {why}; on {", ".join(sorted(where[url])[:3])}' + (' …' if len(where[url]) > 3 else '') for url, _, why in broken]
        lines.append('')
    else:
        lines += ['No broken links.', '']
    if unverified:
        lines += [f'<details><summary>Not verifiable automatically ({len(unverified)}): these sites refuse automated requests</summary>', '']
        lines += [f'- {url} — {why}' for url, _, why in unverified]
        lines += ['', '</details>', '']
    open(out, 'w').write('\n'.join(lines))
    print('\n'.join(lines))
    return 1 if broken else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else 'https://zihengduan.cn', sys.argv[2] if len(sys.argv) > 2 else 'link-report.md'))
