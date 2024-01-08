# reddit_web_scraper_with_localserver.py
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from endpoint_logic_functions import (create_post_logic, get_all_posts_logic, get_post_logic, delete_post_logic,
                                      update_post_logic)
from endpoint_logic_functions import Request, Response


class RequestHandler(BaseHTTPRequestHandler):
    routes = []

    @classmethod
    def add_route(cls, route, method, handler_function):
        cls.routes.append((route, method, handler_function))

    def route_request(self, request):
        parsed_path = urlparse(request.path)
        path_components = parsed_path.path.split('/')
        method = request.method

        for route, route_method, handler_function in self.routes:
            route_components = route.split('/')
            if len(path_components) == len(route_components) and method == route_method:
                data = {}
                for i, component in enumerate(route_components):
                    if component.startswith('{') and component.endswith('}'):
                        data[component[1:-1]] = path_components[i]
                    elif component != path_components[i]:
                        break
                else:
                    return handler_function(request, data)

        return Response(404, 'Endpoint not found')

    def do_POST(self):
        self.handle_request()

    def do_GET(self):
        self.handle_request()

    def do_DELETE(self):
        self.handle_request()

    def do_PUT(self):
        self.handle_request()

    def handle_request(self):
        request = Request(self)
        response = self.route_request(request)
        self.send_response(response.status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response.message).encode())


def generic_handler(logic_function):
    def handler(request, data):
        return Response(200, logic_function(request, data))
    return handler


RequestHandler.add_route('/posts/', 'POST', generic_handler(create_post_logic))
RequestHandler.add_route('/posts/', 'GET', generic_handler(get_all_posts_logic))
RequestHandler.add_route('/posts/{unique_id}/', 'GET', generic_handler(get_post_logic))
RequestHandler.add_route('/posts/{unique_id}/', 'DELETE', generic_handler(delete_post_logic))
RequestHandler.add_route('/posts/{unique_id}/', 'PUT', generic_handler(update_post_logic))


def run_server():
    server_address = ('', 8087)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Server is running on http://localhost:{server_address[1]}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
