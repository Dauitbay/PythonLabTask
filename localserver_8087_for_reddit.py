# localserver_8087_for_reddit.py

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from addiitional_functions import write_error_response
from request_endpoint_logic import (create_post_logic, get_all_posts_logic,
                                    get_post_logic, update_post_logic, delete_post_logic)


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

    def create_post(self, data):
        create_post_logic(self, data)

    def get_all_posts(self, data):
        get_all_posts_logic(self, data)

    def get_post(self, data):
        get_post_logic(self, data)

    def delete_post(self, data):
        delete_post_logic(self, data)

    def update_post(self, data):
        update_post_logic(self, data)


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
