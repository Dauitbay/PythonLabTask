import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import json
import uuid
from urllib.parse import urlparse
from consts import PROG_START_TIME

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATCHING_FILES = [f for f in os.listdir(BASE_DIR) if f.startswith("reddit-")]
REDDIT_FILENAME = os.path.join(BASE_DIR, MATCHING_FILES[0]) if MATCHING_FILES else None


def write_to_file(unique_id, data):
    with open(f"reddit-{PROG_START_TIME}.txt", "a+") as file:
        file.write(unique_id + ";")
        file.write(";".join(map(str, data)) + "\n")


def read_data_from_file():
    data = []
    try:
        with open(os.path.join(BASE_DIR, f"reddit-{PROG_START_TIME}.txt"), "r") as file:
            for line in file:
                data.append(line.strip().split(';'))
    except FileNotFoundError:
        return None
    return data


class RequestHandler(BaseHTTPRequestHandler):

    def set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_POST(self):
        if self.path == '/posts/':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            unique_id = uuid.uuid1().hex[:32]
            decoded_data = json.loads(post_data.decode())
            data_read = read_data_from_file()
            if data_read is not None:
                existing_ids = {item[0] for item in data_read}
                if unique_id not in existing_ids:
                    write_to_file(unique_id, decoded_data)
                    num_of_rows = len(existing_ids) + 1
                    self.set_headers(201)
                    self.wfile.write(json.dumps({'UNIQUE_ID': num_of_rows}).encode())
                else:
                    self.set_headers(409)
                    self.wfile.write(json.dumps({'error': 'Duplicate UNIQUE_ID'}).encode())
            else:
                write_to_file(unique_id, decoded_data)
        elif self.path == '/start_parser/' and REDDIT_FILENAME is None:
            # Trigger the execution of main_reddit_parser.py when /start_parser/ is requested
            subprocess.run(["python", "main_reddit_parser.py", "--posts", "1"])
            self.set_headers(200)
            self.wfile.write(json.dumps({'message': 'main_reddit_parser.py started'}).encode())
        else:
            self.set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path_components = parsed_path.path.split('/')
        if len(path_components) == 4 and path_components[1] == 'posts':
            unique_id = path_components[2]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            data_read = read_data_from_file()
            post_data = next((post for post in data_read if post[0] == unique_id), None)

            if post_data:
                response = {'data': [post_data]}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.set_headers(404)
                self.wfile.write(json.dumps({'error': 'UNIQUE_ID not found'}).encode())

        elif self.path == '/posts/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            data_read = read_data_from_file()
            response = {'data': data_read}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())

    def do_DELETE(self):
        if self.path.startswith('/posts/'):
            if not MATCHING_FILES:
                self.set_headers(404)
                self.wfile.write(json.dumps({'error': 'No matching files found'}).encode())
                return
            data_read = read_data_from_file()
            unique_id = self.path.split('/')[2]
            data = [post for post in data_read if post[0] != unique_id]
            with open(REDDIT_FILENAME, "w") as file:
                for item in data:
                    file.write(";".join(map(str, item)) + "\n")

            self.set_headers(204)
            self.wfile.write(json.dumps({'message': 'Resource deleted successfully'}).encode())
        else:
            self.set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())

    def do_PUT(self):
        parsed_path = urlparse(self.path)
        path_components = parsed_path.path.split('/')
        if len(path_components) == 4 and path_components[1] == 'posts':
            unique_id = path_components[2]

            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            data_read = read_data_from_file()
            post_data_index = next((index for index, post in enumerate(read_data_from_file()) if post[0] == unique_id),
                                   None)
            if post_data_index is not None:
                decoded_data = json.loads(put_data.decode())
                data_read[post_data_index] = [unique_id] + decoded_data
                if not MATCHING_FILES:
                    self.set_headers(404)
                    self.wfile.write(json.dumps({'error': 'No matching files found'}).encode())
                    return
                with open(REDDIT_FILENAME, "w") as file:
                    for item in data_read:
                        file.write(";".join(map(str, item)) + "\n")

                self.set_headers(200)
                self.wfile.write(json.dumps({'message': 'Resource updated successfully'}).encode())
            else:
                self.set_headers(404)
                self.wfile.write(json.dumps({'error': 'UNIQUE_ID not found'}).encode())
        else:
            self.set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())


def run_server():
    server_address = ('', 8087)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Server is running on http://localhost:{server_address[1]}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
