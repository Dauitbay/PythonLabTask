import pytest

from additional_functions import is_valid_data


# Passing valid data
def test_is_valid_data():
    valid_data = {
        "UNIQUE_ID": "abc123def456ghi789jkl012mno345pq",
        "link": "/r/some_subreddit",
        "username": "john_doe",
        "user_cake_data": "Apr 1, 2020",
        "user_post_karma": "1000",
        "user_comment_karma": "500",
        "post_date": "2022-01-01T12:30:00.000000+00:00",
        "number_of_comments": "10",
        "number_of_votes": "50",
        "post_category": "technology"
    }
    assert is_valid_data(valid_data) == True


# Passing invalid_link
def test_invalid_link():
    invalid_data = {
        "UNIQUE_ID": "abc123def456ghi789jkl012mno345pq",
        "link": "123412123",
        "username": "john_doe",
        "user_cake_data": "Apr 1, 2020",
        "user_post_karma": "1000",
        "user_comment_karma": "500",
        "post_date": "2022-01-01T12:30:00.000000+00:00",
        "number_of_comments": "10",
        "number_of_votes": "50",
        "post_category": "technology"
    }
    assert is_valid_data(invalid_data) == False


# Passing invalid username
def test_invalid_username():
    invalid_data = {
        "UNIQUE_ID": "abc123def456ghi789jkl012mno345pq",
        "link": "/r/some_subreddit",
        "username": "121234",
        "user_cake_data": "Apr 1, 2020",
        "user_post_karma": "1000",
        "user_comment_karma": "500",
        "post_date": "2022-01-01T12:30:00.000000+00:00",
        "number_of_comments": "10",
        "number_of_votes": "50",
        "post_category": "technology"
    }
    assert is_valid_data(invalid_data) == False


# Passing invalid user_cake_day
def test_invalid_user_cake_day():
    invalid_data = {
        "UNIQUE_ID": "abc123def456ghi789jkl012mno345pq",
        "link": "/r/some_subreddit",
        "username": "john_doe",
        "user_cake_data": "20231213",
        "user_post_karma": "1000",
        "user_comment_karma": "500",
        "post_date": "2022-01-01T12:30:00.000000+00:00",
        "number_of_comments": "10",
        "number_of_votes": "50",
        "post_category": "technology"
    }
    assert is_valid_data(invalid_data) == False


# Passing invalid user_post_karma
def test_invalid_user_post_karma():
    invalid_data = {
        "UNIQUE_ID": "abc123def456ghi789jkl012mno345pq",
        "link": "/r/some_subreddit",
        "username": "john_doe",
        "user_cake_data": "Apr 1, 2020",
        "user_post_karma": "2023-12-13T12:00:00.000000+00:00",
        "user_comment_karma": "500",
        "post_date": "2022-01-01T12:30:00.000000+00:00",
        "number_of_comments": "10",
        "number_of_votes": "50",
        "post_category": "technology"
    }
    assert is_valid_data(invalid_data) == False


# Passing invalid user_comment_karma
def test_invalid_user_comment_karma():
    invalid_data = {
        "UNIQUE_ID": "abc123def456ghi789jkl012mno345pq",
        "link": "/r/some_subreddit",
        "username": "john_doe",
        "user_cake_data": "Apr 1, 2020",
        "user_post_karma": "10000",
        "user_comment_karma": "2023-12-01T12:00:00.000000+00:00",
        "post_date": "2022-01-01T12:30:00.000000+00:00",
        "number_of_comments": "10",
        "number_of_votes": "50",
        "post_category": "technology"
    }
    assert is_valid_data(invalid_data) == False


# Passing invalid post_data
def test_invalid_post_date():
    invalid_data = {
        "UNIQUE_ID": "abc123def456ghi789jkl012mno345pq",
        "link": "/r/some_subreddit",
        "username": "john_doe",
        "user_cake_data": "Apr 1, 2020",
        "user_post_karma": "10000",
        "user_comment_karma": "500",
        "post_date": "2021/21/03",
        "number_of_comments": "10",
        "number_of_votes": "50",
        "post_category": "technology"
    }
    assert is_valid_data(invalid_data) == False


# Passing invalid number_of_comments
def test_invalid_number_of_comments():
    invalid_data = {
        "UNIQUE_ID": "abc123def456ghi789jkl012mno345pq",
        "link": "/r/some_subreddit",
        "username": "john_doe",
        "user_cake_data": "Apr 1, 2020",
        "user_post_karma": "10000",
        "user_comment_karma": "500",
        "post_date": "2022-01-01T12:00:00.000000+00:00",
        "number_of_comments": "1apple",
        "number_of_votes": "50",
        "post_category": "technology"
    }
    assert is_valid_data(invalid_data) == False


if __name__ == "__main__":
    pytest.main()
