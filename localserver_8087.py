

import uuid
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


def write_to_file(user_data, cur_time):
    with open(f"reddit-{cur_time}.txt", "a+") as file:
        unique_id = uuid.uuid1().hex[:32]
        file.write(unique_id + ";")
        file.write(";".join(user_data) + "\n")

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path_components = parsed_path.path.split('/')

        if path_components[1] == 'posts':
            if len(path_components) == 2:
                # GET http://localhost:8087/posts/
                self._set_headers()
                self.wfile.write(json.dumps(data_store).encode())
            elif len(path_components) == 3:
                # GET http://localhost:8087/posts/<UNIQUE_ID>/
                unique_id = path_components[2]
                post = next((p for p in data_store if p.get('UNIQUE_ID') == unique_id), None)
                if post:
                    self._set_headers()
                    self.wfile.write(json.dumps(post).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Post not found'}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({'error': 'Invalid endpoint'}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())

    def do_POST(self):
        if self.path == '/posts':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = json.loads(post_data.decode())
            unique_id = post_data.get('UNIQUE_ID')
            if not unique_id or any(post.get('UNIQUE_ID') == unique_id for post in data_store):
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid or duplicate UNIQUE_ID'}).encode())
            else:
                data_store.append(post_data)
                self._set_headers(201)
                self.wfile.write(json.dumps({'UNIQUE_ID': unique_id}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())

    def do_DELETE(self):
        if self.path.startswith('/posts/'):
            unique_id = self.path.split('/')[-1]
            global data_store
            data_store = [post for post in data_store if post.get('UNIQUE_ID') != unique_id]
            self._set_headers(204)
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())

    def do_PUT(self):
        if self.path.startswith('/posts/'):
            unique_id = self.path.split('/')[-1]
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = json.loads(post_data.decode())
            for post in data_store:
                if post.get('UNIQUE_ID') == unique_id:
                    post.update(post_data)
                    self._set_headers(204)
                    return
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Post not found'}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())


def run(server_class=HTTPServer, handler_class=RequestHandler, port=8087):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()


