from http.server import BaseHTTPRequestHandler
import requests
from urllib.parse import urlparse, parse_qs

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
REFERER = "https://tvf90.com/"
ORIGIN = "https://tvf90.com"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        target_url = query.get('url', [None])[0]

        if not target_url:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Falta el parametro url")
            return

        # Limpiar posibles caracteres pegados de formato
        target_url = target_url.split(']')[0].split(')')[0].strip()

        headers = {
            "User-Agent": USER_AGENT,
            "Referer": REFERER,
            "Origin": ORIGIN,
            "Accept": "*/*",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site"
        }

        try:
            res = requests.get(target_url, headers=headers, timeout=10)

            if res.status_code != 200:
                self.send_response(res.status_code)
                self.end_headers()
                self.wfile.write(res.content)
                return

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
                self.send_response(200)
                self.send_header('Content-Type', res.headers.get('content-type', 'video/mp2t'))
                self.end_headers()
                self.wfile.write(res.content)

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))
