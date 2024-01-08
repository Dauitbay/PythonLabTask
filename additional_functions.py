# additional_functions.py for localserver
from datetime import datetime
from consts import (REDDIT_FILENAME, PROG_START_TIME, MATCHING_FILES)


def is_valid_data(data):
    def is_valid_date_string(data_to_validate):
        try:
            datetime.strptime(data_to_validate, "%Y-%m-%dT%H:%M:%S.%f%z")
            return True
        except ValueError:
            return False

    def is_valid_month_day_year(date_string):
        try:
            datetime.strptime(date_string, "%b %d, %Y")
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
        "username":  lambda x: isinstance(x, str) and not x.isdigit(),
        "user_cake_data":  is_valid_month_day_year,
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


def write_to_file(data, unique_id=None):
    if MATCHING_FILES and unique_id is not None:
        with open(REDDIT_FILENAME, "a+") as file:
            file.write(unique_id + ";" + ';'.join(f"{value}" for key, value in data.items()) + "\n")
    elif unique_id is None:
        with open(REDDIT_FILENAME, "w") as file:
            for item in data:
                file.write(";".join(map(str, item)) + "\n")
    else:
        with open(f"reddit-{PROG_START_TIME}.txt", "a+") as file:
            file.write(unique_id + ";" + ';'.join(f"{value}" for key, value in data.items()) + "\n")


def convert_list_to_dict(list_data):
    result_list = []
    for input_list in list_data:
        result_dict = {
            "UNIQUE_ID": input_list[0],
            "link": input_list[1],
            "username": input_list[2],
            "user_cake_data": input_list[3],
            "user_post_karma": input_list[4],
            "user_comment_karma": input_list[5],
            "post_date": input_list[6],
            "number_of_comments": input_list[7],
            "number_of_votes": input_list[8],
            "post_category": input_list[9]
        }
        result_list.append(result_dict)

    return result_list


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
