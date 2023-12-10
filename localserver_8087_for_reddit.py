# localserver_8087_for_reddit.py
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import json
import uuid
from urllib.parse import urlparse
from consts import PROG_START_TIME

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATCHING_FILES = [f for f in os.listdir(BASE_DIR) if f.startswith("reddit-")]
REDDIT_FILENAME = os.path.join(BASE_DIR, MATCHING_FILES[0]) if MATCHING_FILES else None


def is_valid_post_data(data):
    if not isinstance(data, list) or len(data) != 6:
        return False
    # Checking if the 0 field is a valid path
    if not isinstance(data[0], str) or not data[0].startswith("/"):
        return False
    # Checking if the 1field is a valid string
    if not isinstance(data[1], str):
        return False
    # Checking if the 2 field is a valid integer
    try:
        int(data[2].replace(',', ''))
    except ValueError:
        return False
    # Checking if the 3 field is a valid datetime string
    try:
        datetime.strptime(data[3], "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        return False
    # Checking if the 4 field and seventh 5 are valid integers
    try:
        int(data[4])
        int(data[5])
    except ValueError:
        return False
    return True


def write_to_file(unique_id, data):
    if MATCHING_FILES:
        with open(REDDIT_FILENAME, "a+") as file:
            file.write(unique_id + ";")
            file.write(";".join(map(str, data)) + "\n")
    else:
        with open(f"reddit-{PROG_START_TIME}.txt", "a+") as file:
            file.write(unique_id + ";")
            file.write(";".join(map(str, data)) + "\n")


def read_data_from_file():
    data = []
    try:
        with open(os.path.join(BASE_DIR, REDDIT_FILENAME), "r") as file:
            for line in file:
                data.append(line.strip().split(';'))
    except FileNotFoundError:
        return None
    return data


def set_headers(handler, status=200, content_type='application/json'):
    handler.send_response(status)
    handler.send_header('Content-type', content_type)
    handler.end_headers()


def write_error_response(handler, status, message):
    set_headers(handler, status)
    handler.wfile.write(json.dumps({'error': message}).encode())


class RequestHandler(BaseHTTPRequestHandler):

    def if_no_reddit_file(self):
        if not MATCHING_FILES:
            write_error_response(self, 404, 'No matching files found')
            return

    def do_POST(self):
        if self.path == '/posts/':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            unique_id = uuid.uuid1().hex[:32]
            decoded_data = json.loads(post_data.decode())
            if not is_valid_post_data(decoded_data):
                write_error_response(self, 400, 'Invalid data format')
                return
            data_read = read_data_from_file()
            if data_read is not None:
                existing_ids = {item[0] for item in data_read}
                if unique_id not in existing_ids:
                    write_to_file(unique_id, decoded_data)
                    num_of_rows = len(existing_ids) + 1
                    set_headers(self, 201)
                    self.wfile.write(json.dumps({'UNIQUE_ID': num_of_rows}).encode())
                else:
                    write_error_response(self, 409, 'Duplicate UNIQUE_ID')
            else:
                write_to_file(unique_id, decoded_data)
        else:
            write_error_response(self, 404, 'Endpoint not found')

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path_components = parsed_path.path.split('/')
        if len(path_components) == 4 and path_components[1] == 'posts':
            unique_id = path_components[2]
            set_headers(self, 200)
            data_read = read_data_from_file()
            post_data = next((post for post in data_read if post[0] == unique_id), None)

            if post_data:
                response = {'data': [post_data]}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                write_error_response(self, 404, 'UNIQUE_ID not found')

        elif self.path == '/posts/':
            set_headers(self, 200)
            data_read = read_data_from_file()
            response = {'data': data_read}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            write_error_response(self, 404, 'Endpoint not found')

    def do_DELETE(self):
        if self.path.startswith('/posts/'):
            self.if_no_reddit_file()
            data_read = read_data_from_file()
            unique_id = self.path.split('/')[2]
            data = [post for post in data_read if post[0] != unique_id]
            with open(REDDIT_FILENAME, "w") as file:
                for item in data:
                    file.write(";".join(map(str, item)) + "\n")

            set_headers(self, 204)
            self.wfile.write(json.dumps({'message': 'Resource deleted successfully'}).encode())
        else:
            write_error_response(self, 404, 'Endpoint not found')

    def do_PUT(self):
        parsed_path = urlparse(self.path)
        path_components = parsed_path.path.split('/')
        if len(path_components) == 4 and path_components[1] == 'posts':
            unique_id = path_components[2]

            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            data_read = read_data_from_file()

            post_data_index = next((index for index, post in enumerate(data_read) if post[0] == unique_id),
                                   None)
            if post_data_index is not None:
                decoded_data = json.loads(put_data.decode())
                print(decoded_data)
                if not is_valid_post_data(decoded_data):
                    write_error_response(self, 400, 'Invalid data format')
                    return
                data_read[post_data_index] = [unique_id] + decoded_data
                self.if_no_reddit_file()
                with open(REDDIT_FILENAME, "w") as file:
                    for item in data_read:
                        file.write(";".join(map(str, item)) + "\n")

                set_headers(self, 200)
                self.wfile.write(json.dumps({'message': 'Resource updated successfully'}).encode())
            else:
                write_error_response(self, 404, 'UNIQUE_ID not found')
        else:
            write_error_response(self, 404, 'Endpoint not found')


def run_server():
    server_address = ('', 8087)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Server is running on http://localhost:{server_address[1]}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
