#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer

from abm_helper import AbmClient
from store import KeyStore

abmc = AbmClient()
key_cache = KeyStore()

class RequestHandler(BaseHTTPRequestHandler):
    def send(self, status, body):
        content_type = "application/octet-stream"

        if type(body) == str:
            content_type = "text/plain"
            body = bytes(body, "utf8")

        self.protocol_version = "HTTP/1.1"
        self.send_response(status)
        self.send_header("Content-Length", len(body))
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body)
        return

    def do_GET(self):
        segs = self.path.split('/')

        if (len(segs) == 2):
            kid = segs[1].split('?')[0]

            if len(kid) == 0:
                return self.send(200, "Hello world!")

            try:
                cached = key_cache.get(kid)
                if cached:
                    print("cached", kid)
                    return self.send(200, cached)
                print("new", kid)
                key_payload = abmc._get_key_from_id(kid)
                key_cache.set(kid, key_payload)
                return self.send(200, key_payload)
            except Exception as e:
                print(e)

        return self.send(400, 'Bad Request')

def run():
    server = ('127.0.0.1', 8088)
    httpd = HTTPServer(server, RequestHandler)
    httpd.serve_forever()
run()