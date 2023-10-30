from datetime import datetime
import os
import pytest
from unittest.mock import  patch
import requests
import validators
from main_reddit import delete_reddit_and_mylog_file, get_current_time, generate_unique_id, get_next_url, collect_return_posts_num
from main_reddit import MAIN_URL, HEADERS

# Constants for testing
FILE_NAME = "reddit-test_YYMMddHHMM.txt"
REDDIT_WEBPAGE_ADDRESS = "https://www.reddit.com"


def test_generate_unique_id_valid_format():
    unique_id = generate_unique_id()
    assert len(unique_id) == 32
    assert unique_id.isalnum()
    int(unique_id, 16)


def test_generate_unique_id_invalid_format():
    invalid_id = "invalid_id"
    with pytest.raises(ValueError):
        int(invalid_id, 16)  


def test_multiple_unique_ids():
    unique_ids = [generate_unique_id() for _ in range(100)]
    assert len(unique_ids) == len(set(unique_ids))


@pytest.fixture
def create_sample_files():
    file_names = ["reddit-202310290830.txt", "my_logfile.log", "other_file.txt"]
    for file_name in file_names:
        open(file_name, "w").close()
    yield
    for file_name in file_names:
        if os.path.exists(file_name):
            os.remove(file_name)


def test_delete_existing_file(create_sample_files):
    assert os.path.isfile("reddit-202310290830.txt")
    assert os.path.isfile("my_logfile.log")
    assert os.path.isfile("other_file.txt")
    delete_reddit_and_mylog_file()
    assert not os.path.exists("reddit-202310290830.txt")
    assert not os.path.exists("my_logfile.log")
    assert os.path.exists("other_file.txt")
    if os.path.exists("other_file.txt"):
        os.remove("other_file.txt")


def test_get_current_time_valid_format():
    timestamp = get_current_time()
    expected_format = "%Y_%m_%d_%H_%M"
    datetime.strptime(timestamp, expected_format)  


def test_get_current_time_invalid_format():
    invalid_timestamp = "invalid_timestamp"
    expected_format = "%Y_%m_%d_%H_%M"
    with pytest.raises(ValueError):
        datetime.strptime(invalid_timestamp, expected_format) 


def test_get_next_url_response():
    result = get_next_url(MAIN_URL)
    response = validators.url(result)
    assert response == True


def test_get_post_data_timeout(): 
    with patch("requests.get", side_effect=requests.exceptions.Timeout("Request timed out")):
        with pytest.raises(requests.exceptions.Timeout):
            result = requests.get(url=MAIN_URL, headers=HEADERS, timeout=10)
            collect_return_posts_num(REDDIT_WEBPAGE_ADDRESS, 10, FILE_NAME)


def test_get_post_data_no_timeout():
    result = requests.get(url=MAIN_URL, headers=HEADERS, timeout=10)
    post_result = collect_return_posts_num(MAIN_URL, 1, FILE_NAME)
    # Assuming one iteration reduces number_of_posts by 1
    assert post_result == 0  
    delete_reddit_and_mylog_file()


if __name__ == "__main__":
    pytest.main()

