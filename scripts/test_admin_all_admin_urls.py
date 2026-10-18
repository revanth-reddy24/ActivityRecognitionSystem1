import urllib.request, urllib.parse, http.cookiejar
from html.parser import HTMLParser

LOGIN_URL = 'http://127.0.0.1:8000/login/'
BASE = 'http://127.0.0.1:8000'
ENDPOINTS = [
    '/admin-panel/',
    '/admin-panel/users/',
    '/admin-panel/users/1/',
    '/admin-panel/reports/',
    '/admin-panel/system-config/',
    '/admin-panel/model-management/',
    '/admin-panel/environments/',
    '/admin-panel/audit-logs/',
]
USERNAME = 'admin'
PASSWORD = 'adminpass'

class CSRFParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.csrf = None
    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            d = dict(attrs)
            if d.get('name') == 'csrfmiddlewaretoken':
                self.csrf = d.get('value')

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Get login page
try:
    resp = opener.open(LOGIN_URL)
except Exception as e:
    print('Error connecting to server:', e)
    raise SystemExit(1)

html = resp.read().decode('utf-8', 'ignore')
parser = CSRFParser()
parser.feed(html)
csrf = parser.csrf
print('Found csrf:', csrf)

if not csrf:
    print('CSRF token not found; cannot login programmatically.')
    raise SystemExit(1)

# login
login_data = urllib.parse.urlencode({
    'username': USERNAME,
    'password': PASSWORD,
    'csrfmiddlewaretoken': csrf,
}).encode('utf-8')
headers = {
    'Referer': LOGIN_URL,
    'Content-Type': 'application/x-www-form-urlencoded'
}
req = urllib.request.Request(LOGIN_URL, data=login_data, headers=headers)
resp = opener.open(req)
print('Login response URL:', resp.geturl())

# request each endpoint
for ep in ENDPOINTS:
    url = BASE + ep
    try:
        r = opener.open(url)
        content = r.read().decode('utf-8', 'ignore')
        print(f"{ep} -> {r.getcode()} {len(content)} bytes (final: {r.geturl()})")
    except urllib.error.HTTPError as he:
        print(f"{ep} -> HTTPError {he.code}: {he.reason}")
    except Exception as e:
        print(f"{ep} -> Error: {e}")
