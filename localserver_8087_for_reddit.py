from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import uuid
from urllib.parse import urlparse
from consts import (PROG_START_TIME, BASE_DIR, MATCHING_FILES, REDDIT_FILENAME)


def is_valid_data(data):

    def is_valid_date_string(data_to_validate):
        try:
            datetime.strptime(data_to_validate, "%Y-%m-%dT%H:%M:%S.%f%z")
            return True
        except ValueError:
            return False

    def is_valid_integer_string(data_to_validate):
        try:
            int(data_to_validate.replace(',', ''))
            return True
        except ValueError:
            return False
    validation_rules = {
        "UNIQUE_ID": lambda x: isinstance(x, str) and len(x) == 32,
        "link": lambda x: isinstance(x, str) and x.startswith("/r/"),
        "username": lambda x: isinstance(x, str),
        "user_cake_data": is_valid_date_string,
        "user_post_karma": is_valid_integer_string,
        "user_comment_karma": is_valid_integer_string,
        "post_date": is_valid_date_string,
        "number_of_comments": is_valid_integer_string,
        "number_of_votes": is_valid_integer_string,
        "post_category": lambda x: isinstance(x, str),
    }
    for field, validation_rule in validation_rules.items():
        if "UNIQUE_ID" not in data:
            continue

        value = data[field]
        if not validation_rule(value):
            return False

    return True


def write_to_file(unique_id, data):
    if MATCHING_FILES:
        with open(REDDIT_FILENAME, "a+") as file:
            file.write(unique_id + ";" + ';'.join(f"{value}" for key, value in data.items()) + "\n")
    else:
        with open(f"reddit-{PROG_START_TIME}.txt", "a+") as file:
            file.write(unique_id + ";" + ';'.join(f"{value}" for key, value in data.items()) + "\n")


def read_data_from_file():
    data = []
    try:
        if REDDIT_FILENAME is not None:
            with open(REDDIT_FILENAME, "r") as file:
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
    routes = []

    @classmethod
    def add_route(cls, route, method, handler_method):
        cls.routes.append((route, method, handler_method))

    def route_request(self):

        parsed_path = urlparse(self.path)
        path_components = parsed_path.path.split('/')
        method = self.command
        for route, route_method, handler_method in self.routes:
            route_components = route.split('/')
            if len(path_components) == len(route_components) and method == route_method:
                data = {}
                for i, component in enumerate(route_components):
                    if component.startswith('{') and component.endswith('}'):
                        data[component[1:-1]] = path_components[i]
                    elif component != path_components[i]:
                        break
                else:
                    handler_function = getattr(self, handler_method)
                    handler_function(data)
                    return
        write_error_response(self, 404, 'Endpoint not found')

    def do_POST(self):
        self.route_request()

    def do_GET(self):
        self.route_request()

    def do_DELETE(self):
        self.route_request()

    def do_PUT(self):
        self.route_request()

    def rewrite_data_to_file(self, data_read):
        with open(REDDIT_FILENAME, "w") as file:
            for item in data_read:
                file.write(";".join(map(str, item)) + "\n")

    def create_post(self, data):
        # Handler for creating a post
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        unique_id = uuid.uuid1().hex[:32]
        decoded_data = json.loads(post_data.decode())
        if not is_valid_data(decoded_data):
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

    def get_all_posts(self, data):
        set_headers(self, 200)
        data_read = read_data_from_file()
        response = {'data': data_read}
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def get_post(self, data):
        unique_id = data.get('unique_id')
        set_headers(self, 200)
        data_read = read_data_from_file()
        post_data = next((post for post in data_read if post[0] == unique_id), None)

        if post_data:
            response = {'data': [post_data]}
            self.wfile.write(json.dumps(response).encode())
        else:
            write_error_response(self, 404, 'UNIQUE_ID not found')

    def delete_post(self, data):
        parsed_path = urlparse(self.path)
        path_components = parsed_path.path.split('/')
        unique_id = path_components[-2]
        data_read = read_data_from_file()
        data = [post for post in data_read if post[0] != unique_id]
        if data_read != data:
            self.rewrite_data_to_file(data)
            set_headers(self, 204)
            self.wfile.write(json.dumps({'message': 'Resource deleted successfully'}).encode('utf-8'))
        else:
            write_error_response(self, 404, 'UNIQUE_ID not found')

    def update_post(self, data):
        unique_id = data.get('unique_id')
        content_length = int(self.headers['Content-Length'])
        put_data = self.rfile.read(content_length)
        data_read = read_data_from_file()
        post_data_index = next((index for index, post in enumerate(data_read) if post[0] == unique_id), None)
        if post_data_index is not None:
            decoded_data = json.loads(put_data.decode())
            if not is_valid_data(decoded_data):
                write_error_response(self, 400, 'Invalid data format')
                return
            with open(REDDIT_FILENAME, "a+") as file:
                file.write(unique_id + ";" + ';'.join(f"{value}" for key, value in decoded_data.items()) + "\n")
            set_headers(self, 200)
            self.wfile.write(json.dumps({'message': 'Resource updated successfully'}).encode())
        else:
            write_error_response(self, 404, 'UNIQUE_ID not found')


RequestHandler.add_route('/posts/', 'POST', 'create_post')
RequestHandler.add_route('/posts/', 'GET', 'get_all_posts')
RequestHandler.add_route('/posts/{unique_id}/', 'GET', 'get_post')
RequestHandler.add_route('/posts/{unique_id}/', 'DELETE', 'delete_post')
RequestHandler.add_route('/posts/{unique_id}/', 'PUT', 'update_post')
# RequestHandler.add_route('/new_endpoint/', 'POST', 'function_name_for_handling_endpoint')


def run_server():
    server_address = ('', 8087)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Server is running on http://localhost:{server_address[1]}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
