# endpoint_logic_functions.py
import uuid
import json
from additional_functions import convert_list_to_dict, read_data_from_file, is_valid_data, write_to_file


class Response:

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def error_response(self, handler):
        self.set_headers(handler, self.status_code)
        handler.wfile.write(json.dumps({'error': self.message}).encode())

    @staticmethod
    def set_headers(handler, status=200, content_type='application/json'):
        handler.send_response(status)
        handler.send_header('Content-type', content_type)
        handler.end_headers()


class Request:
    def __init__(self, handler):
        self.handler = handler

    def get_data(self):
        content_length = int(self.handler.headers['Content-Length'])
        post_data = self.handler.rfile.read(content_length)
        return json.loads(post_data.decode())

    @property
    def path(self):
        return self.handler.path

    @property
    def method(self):
        return self.handler.command


def create_post_logic(request, data):
    content_length = int(request.handler.headers['Content-Length'])
    post_data = request.handler.rfile.read(content_length)
    unique_id = uuid.uuid1().hex[:32]
    decoded_data = json.loads(post_data.decode())

    if not is_valid_data(decoded_data):
        return Response(400, 'Invalid data format').error_response(request.handler)

    data_read = read_data_from_file()
    if data_read is not None:
        existing_ids = {item[0] for item in data_read}
        if unique_id not in existing_ids:
            write_to_file(decoded_data, unique_id)
            num_of_rows = len(existing_ids) + 1
            Response.set_headers(request.handler, 201)
            return request.handler.wfile.write(json.dumps({'UNIQUE_ID': num_of_rows}).encode())
        else:
            return Response(409, 'Duplicate UNIQUE_ID').error_response(request.handler)
    else:
        return write_to_file(decoded_data, unique_id)


def get_all_posts_logic(request, data):
    Response.set_headers(request.handler, 200)
    data_read = convert_list_to_dict(read_data_from_file())
    response = {'data': data_read}
    return request.handler.wfile.write(json.dumps(response).encode('utf-8'))


def get_post_logic(request, data):
    unique_id = data.get('unique_id')
    Response.set_headers(request.handler, 200)
    data_read = read_data_from_file()
    post_data = next((post for post in data_read if post[0] == unique_id), None)

    if post_data:
        response = {'data': convert_list_to_dict([post_data])}
        return request.handler.wfile.write(json.dumps(response).encode())
    else:
        return Response(404, 'UNIQUE_ID not found').error_response(request.handler)


def delete_post_logic(request, data):
    unique_id = data.get('unique_id')
    data_read = read_data_from_file()
    data = [post for post in data_read if post[0] != unique_id]

    if data_read != data:
        write_to_file(data)
        Response.set_headers(request.handler, 204)
        return request.handler.wfile.write(json.dumps({'message': 'Resource deleted successfully'}).encode('utf-8'))
    else:
        return Response(404, 'UNIQUE_ID not found').error_response(request.handler)


def update_post_logic(request, data):
    unique_id = data.get('unique_id')
    content_length = int(request.handler.headers['Content-Length'])
    put_data = request.handler.rfile.read(content_length)
    data_read = read_data_from_file()
    post_data_index = next((index for index, post in enumerate(data_read) if post[0] == unique_id), None)

    if post_data_index is not None:
        decoded_data = json.loads(put_data.decode())
        if not is_valid_data(decoded_data):
            return Response(400, 'Invalid data format').error_response(request.handler)

        data_read[post_data_index] = [unique_id] + [decoded_data.get(key, '') for key in
                                                    ['link', 'username', 'user_cake_data', 'user_post_karma',
                                                     'user_comment_karma', 'post_date', 'number_of_comments',
                                                     'number_of_votes', 'post_category']]
        convert_list_to_dict(data_read)
        write_to_file(data_read)
        Response.set_headers(request.handler, 200)
        return request.handler.wfile.write(json.dumps({'message': 'Resource updated successfully'}).encode())
    else:
        return Response(404, 'UNIQUE_ID not found').error_response(request.handler)
