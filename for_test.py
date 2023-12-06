from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import json
import datetime
import uuid
# import threading
# import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
prog_start_time = datetime.datetime.now().strftime("%Y%m%d")


def write_to_file(unique_id, data):
    with open(f"reddit-{prog_start_time}.txt", "a+") as file:
        file.write(unique_id + ";")
        file.write(";".join(map(str, data)) + "\n")


def read_data_from_file():
    # Read data from the file and return it as a list
    data = []
    try:
        with open(os.path.join(BASE_DIR, f"reddit-{prog_start_time}.txt"), "r") as file:
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
            if os.path.exists(os.path.join(BASE_DIR, f"reddit-{prog_start_time}.txt")):
                data_read = read_data_from_file()
                existing_ids = {item[0] for item in data_read}

                unique_id = uuid.uuid1().hex[:32]
                if unique_id not in existing_ids:
                    decoded_data = json.loads(post_data.decode())
                    write_to_file(unique_id, decoded_data)
                    self.set_headers(201)
                    self.wfile.write(json.dumps({'UNIQUE_ID': len(existing_ids)}).encode())
                else:
                    # Duplicate UNIQUE_ID, return a 409 (Conflict) status
                    self.set_headers(409)
                    self.wfile.write(json.dumps({'error': 'Duplicate UNIQUE_ID'}).encode())
            else:
                unique_id = uuid.uuid1().hex[:32]
                decoded_data = json.loads(post_data.decode())
                write_to_file(unique_id, decoded_data)

        else:
            self.set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())

    def do_GET(self):
        if self.path == '/posts/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            data = read_data_from_file()
            response = {'data': data}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self.set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())

    def do_DELETE(self):
        if self.path.startswith('/posts/'):
            matching_files = [f for f in os.listdir(BASE_DIR) if f.startswith("reddit-")]
            if not matching_files:
                self.set_headers(404)
                self.wfile.write(json.dumps({'error': 'No matching files found'}).encode())
                return

            unique_id = self.path.split('/')[2]
            filename = os.path.join(BASE_DIR, matching_files[0])
            # Read data from the file
            data = read_data_from_file()
            # Filter out the data with the specified unique_id
            data = [post for post in data if post[0] != unique_id]
            # Write the modified data back to the file
            with open(filename, "w") as file:
                for item in data:
                    file.write(";".join(map(str, item)) + "\n")

                # Respond with a 204 status code
            self.set_headers(204)
            self.wfile.write(json.dumps({'message': 'Resource deleted successfully'}).encode())

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
