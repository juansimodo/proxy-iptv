from http.server import BaseHTTPRequestHandler
import requests
from urllib.parse import urlparse, parse_qs

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
REFERER = "https://tvf90.com/"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        target_url = query.get('url', [None])[0]

        if not target_url:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Falta la URL")
            return

        headers = {
            "User-Agent": USER_AGENT,
            "Referer": REFERER
        }

        try:
            res = requests.get(target_url, headers=headers, timeout=10)

            if ".m3u8" in target_url:
                content = res.text
                base_url = target_url.rsplit('/', 1)[0] + '/'
                host = self.headers.get('Host')
                lines = content.splitlines()
                new_lines = []
                for line in lines:
                    if line.startswith("#") or not line.strip():
                        new_lines.append(line)
                    else:
                        segment_url = line if line.startswith("http") else base_url + line
                        new_lines.append(f"https://{host}/api?url={segment_url}")

                body = "\n".join(new_lines).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/x-mpegURL')
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(res.status_code)
                self.send_header('Content-Type', res.headers.get('content-type', 'video/mp2t'))
                self.end_headers()
                self.wfile.write(res.content)

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))
