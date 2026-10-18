import urllib.request, urllib.parse, http.cookiejar
from html.parser import HTMLParser

LOGIN_URL = 'http://127.0.0.1:8000/login/'
ADMIN_URL = 'http://127.0.0.1:8000/admin-panel/'
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
resp = opener.open(LOGIN_URL)
html = resp.read().decode('utf-8', 'ignore')
parser = CSRFParser()
parser.feed(html)
csrf = parser.csrf
print('Found csrf:', csrf)

if not csrf:
    print('CSRF token not found; cannot login programmatically.')
else:
    data = urllib.parse.urlencode({
        'username': USERNAME,
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf,
    }).encode('utf-8')
    headers = {
        'Referer': LOGIN_URL,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    req = urllib.request.Request(LOGIN_URL, data=data, headers=headers)
    resp = opener.open(req)
    # After login, request admin page
    admin_resp = opener.open(ADMIN_URL)
    content = admin_resp.read().decode('utf-8', 'ignore')
    print('Admin page URL:', admin_resp.geturl())
    print('Status length:', len(content))
    print(content[:1000])
