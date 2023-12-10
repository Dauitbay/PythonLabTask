import json
import requests
import pytest
from datetime import datetime

BASE_URL = "http://localhost:8087/posts/"

VALID_POST_DATA = [
    "/r/mildlyinteresting/comments/17yblio/found_bill_of_sale_on_1919_model_t/",
    "big_d_usernametaken",
    "11376",
    "2023-11-18T17:39:18.726000+0000",
    "3992",
    "99290"
]


@pytest.fixture
def valid_unique_id():
    return "valid_unique_id"


def test_do_post(valid_unique_id):
    response = requests.post(
        BASE_URL,
        data=json.dumps(VALID_POST_DATA),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 201
    assert "UNIQUE_ID" in response.json()


def test_do_get(valid_unique_id):
    response = requests.get(BASE_URL + valid_unique_id)
    if response.status_code != 404:
        assert response.status_code == 200
        assert "data" in response.json()
    else:
        assert response.status_code == 404
        assert "error" in response.json()

def test_do_delete(valid_unique_id):
    response = requests.delete(BASE_URL + valid_unique_id)
    assert response.status_code == 204


def test_do_put(valid_unique_id):
    updated_data = [
        "/new_path",
        "new_string",
        "42",
        "2023-11-18T18:00:00.000000+0000",
        "100",
        "200"
    ]
    response = requests.put(
        BASE_URL + valid_unique_id,
        data=json.dumps(updated_data),
        headers={"Content-Type": "application/json"}
    )
    if response.status_code != 404:
        assert response.status_code == 200
        assert "message" in response.json()
    else:
        assert response.status_code == 404
        assert "error" in response.json()


def test_do_post_invalid_data():
    invalid_data = "invalid_data"
    response = requests.post(
        BASE_URL,
        data=json.dumps(invalid_data),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert "error" in response.json()


def test_do_get_nonexistent_id():
    nonexistent_id = "nonexistent_id"
    response = requests.get(BASE_URL + nonexistent_id)
    assert response.status_code == 404
    assert "error" in response.json()


def test_do_put_nonexistent_id():
    nonexistent_id = "nonexistent_id"
    updated_data = [
        "/new_path",
        "new_string",
        "42",
        "2023-11-18T18:00:00.000000+0000",
        "100",
        "200"
    ]
    response = requests.put(
        BASE_URL + nonexistent_id,
        data=json.dumps(updated_data),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 404
    assert "error" in response.json()


if __name__ == "__main__":
    pytest.main()
