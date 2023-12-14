# This module is for localserver_8087_for_reddit.py

import uuid
import json
from urllib.parse import urlparse
from consts import REDDIT_FILENAME

from addiitional_functions import (write_error_response, set_headers, convert_list_to_dict,
                                   read_data_from_file, is_valid_data, write_to_file)


def create_post_logic(header_from_local, data):
    content_length = int(header_from_local.headers['Content-Length'])
    post_data = header_from_local.rfile.read(content_length)
    unique_id = uuid.uuid1().hex[:32]
    decoded_data = json.loads(post_data.decode())
    if not is_valid_data(decoded_data):
        return write_error_response(header_from_local, 400, 'Invalid data format')

    data_read = read_data_from_file()
    if data_read is not None:
        existing_ids = {item[0] for item in data_read}
        if unique_id not in existing_ids:
            write_to_file(decoded_data, unique_id)
            num_of_rows = len(existing_ids) + 1
            set_headers(header_from_local, 201)
            return header_from_local.wfile.write(json.dumps({'UNIQUE_ID': num_of_rows}).encode())
        else:
            return write_error_response(header_from_local, 409, 'Duplicate UNIQUE_ID')
    else:
        return write_to_file(decoded_data, unique_id)


def get_all_posts_logic(get_header, data):
    set_headers(get_header, 200)
    data_read = convert_list_to_dict(read_data_from_file())
    response = {'data': data_read}
    return get_header.wfile.write(json.dumps(response).encode('utf-8'))


def get_post_logic(get_post_header, data):
    unique_id = data.get('unique_id')
    set_headers(get_post_header, 200)
    data_read = read_data_from_file()
    post_data = next((post for post in data_read if post[0] == unique_id), None)

    if post_data:
        response = {'data': convert_list_to_dict([post_data])}
        return get_post_header.wfile.write(json.dumps(response).encode())
    else:
        return write_error_response(get_post_header, 404, 'UNIQUE_ID not found')


def delete_post_logic(delete_header, data):
    parsed_path = urlparse(delete_header.path)
    path_components = parsed_path.path.split('/')
    unique_id = path_components[-2]
    data_read = read_data_from_file()
    data = [post for post in data_read if post[0] != unique_id]
    if data_read != data:
        write_to_file(data)
        set_headers(delete_header, 204)
        return delete_header.wfile.write(json.dumps({'message': 'Resource deleted successfully'}).encode('utf-8'))
    else:
        return write_error_response(delete_header, 404, 'UNIQUE_ID not found')


def update_post_logic(update_header, data):
    unique_id = data.get('unique_id')
    content_length = int(update_header.headers['Content-Length'])
    put_data = update_header.rfile.read(content_length)
    data_read = read_data_from_file()
    post_data_index = next((index for index, post in enumerate(data_read) if post[0] == unique_id), None)
    if post_data_index is not None:
        decoded_data = json.loads(put_data.decode())
        if not is_valid_data(decoded_data):
            return write_error_response(update_header, 400, 'Invalid data format')
        data_read[post_data_index] = [unique_id] + [decoded_data.get(key, '') for key in
                                                    ['link', 'username', 'user_cake_data', 'user_post_karma',
                                                     'user_comment_karma', 'post_date', 'number_of_comments',
                                                     'number_of_votes', 'post_category']]
        convert_list_to_dict(data_read)
        write_to_file(data_read)
        set_headers(update_header, 200)
        return update_header.wfile.write(json.dumps({'message': 'Resource updated successfully'}).encode())
    else:
        return write_error_response(update_header, 404, 'UNIQUE_ID not found')
