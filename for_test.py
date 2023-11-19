from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import datetime
import uuid
import threading
from main_reddit_parser import logger


class RequestHandler(BaseHTTPRequestHandler):

    def set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def write_to_file(self, unique_id, data):
        prog_start_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
        with open(f"reddit-{prog_start_time}.txt", "a+") as file:
            file.write(unique_id + ";")
            file.write(";".join(map(str, data)) + "\n")

    def do_POST(self):
        if self.path == '/posts':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                decoded_data = json.loads(post_data.decode())
                unique_id = uuid.uuid1().hex[:32]
                self.write_to_file(unique_id, decoded_data)
                self.set_headers(201)
                self.wfile.write(json.dumps({'UNIQUE_ID': unique_id}).encode())
            except json.JSONDecodeError as e:
                self.set_headers(400)
                self.wfile.write(json.dumps({'error': f'Error decoding JSON: {str(e)}'}).encode())
        else:
            self.set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())


def run_server():
    server_address = ('', 8087)
    httpd = HTTPServer(server_address, RequestHandler)
    logger.info("Server is running on http://localhost:8087")
    httpd.serve_forever()
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.start()


if __name__ == "__main__":
    run_server()




