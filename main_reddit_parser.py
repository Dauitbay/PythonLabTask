"""main_reddit_parser.py does request to reddit.com (MONTH TOP posts) to get:

    - post URL;
    - username;
    - user karma;
    - user cake day;
    - post karma;
    - comment karma;
    - post date;
    - number of comments;
    - number of votes;
    - post category---> I could not GET this one only.
    And saves them using RESTful service in reddit-YYYYMMDDHHMM.txt giving UNIQUE_ID
    to every USER COLLECTED DATA.
    AROUND 8-9 minutes required to gather 100 user data.
    This module has additional <consts.py> module for CONSTANTS
"""

from time import sleep
from random import randint
import argparse
import os
import os.path
import logging
import sys
import requests
from bs4 import BeautifulSoup

from consts import (REDDIT_WEBPAGE_ADDRESS, HTML_PARSER, SHREDDIT_APP, SHREDDIT_POST, SOUP_FIND_CLASS_NAME,
                    REQUEST_HEADERS, GET_POST_DATA_FINDALL_CLASS, NUMBER_OF_POSTS_NEEDED_TO_GET,
                    PERIOD_COMMAND_LINE, CATEGOTY_COMMAND_LINE, AUTHOR_PROFILE_FIND, LOG_FILE_NAME,
                    AUTHOR_PROFILE_FIND_CLASS_TEXT_12, AUTHOR_PROFILE_FIND_CLASS_TEXT_14, conn, server_headers)
import http.client
import json


logging.basicConfig(
    level=logging.INFO,
    filename=LOG_FILE_NAME,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S")
logger = logging.getLogger("scraper")


def delete_reddit_and_my_logfile():
    for file_name in os.listdir("."):
        if file_name.startswith(("reddit-", "my_logfile.log")):
            os.remove(file_name)


# Finding URL of next page and send it to get_remaining_posts_num func. through main func.
def get_next_url(url: str):
    create_next_url = ""
    try:
        next_page_req = requests.get(url=url, headers=REQUEST_HEADERS, timeout=10)
        logger.info("Loaded next pages url {}".format(url))
        next_page_soup = BeautifulSoup(next_page_req.text, HTML_PARSER)
        sleep(randint(0, 1))
        find_next_url = (
            next_page_soup.find(SHREDDIT_APP, class_=SOUP_FIND_CLASS_NAME)
            .find("faceplate-partial", attrs={"slot": "load-after"})
            .get("src"))
        create_next_url = REDDIT_WEBPAGE_ADDRESS + str(find_next_url)
    except requests.exceptions.Timeout:
        logger.info("TIMED OUT doing request to next page")
    return create_next_url


def does_post_has_restrictions(soup: BeautifulSoup):
    author_link = soup.find('a', class_='author-name')
    if author_link is None:
        logger.info("Age restriction. Could not get access to authors profile.")
        return True
    post_author_profile_url = REDDIT_WEBPAGE_ADDRESS + author_link.get('href')
    try:
        author_profile_request = requests.get(url=post_author_profile_url, headers=REQUEST_HEADERS, timeout=10)
    except requests.exceptions.Timeout:
        logger.error("TIMED OUT doing post_author_profile_request")
        return True
    soup_author_profile = BeautifulSoup(author_profile_request.text, HTML_PARSER)
    author_profile = soup_author_profile.find(AUTHOR_PROFILE_FIND)
    if author_profile is None:
        logger.info(" Author is BLOCKED or HTML attribute is changed. Could not access the author's profile.")
        return True
    return False


def send_data_to_server(data):
    print(data)
    if not data:
        logger.warning("Attempted to send empty data to the server.")
        return

    connect = http.client.HTTPConnection('localhost', 8087, timeout=10)
    ser_headers = {'Content-type': 'application/json'}
    try:
        encoded_data = json.dumps(data).encode('utf-8')
        connect.request('POST', '/posts/', body=encoded_data, headers=ser_headers)
        response = connect.getresponse()
        logger.info("Response to POST: {}".format(response.read().decode('utf-8')))
    except http.client.RemoteDisconnected as e:
        logger.error(f"RemoteDisconnected: {e}")
    except Exception as e:
        logger.error(f"Error sending data to server: {e}")
    finally:
        connect.close()


# Gathering required data from posts and returning num_of_posts
def get_remaining_posts_num(posts_url: str, number_of_posts: int):
    try:
        result = requests.get(url=posts_url, headers=REQUEST_HEADERS, timeout=10)
    except requests.exceptions.Timeout:
        logger.error("TIMED OUT doing posts_url_request")
        return number_of_posts
    soup = BeautifulSoup(result.text, HTML_PARSER)
    user_info = soup.find(SHREDDIT_APP, class_=SOUP_FIND_CLASS_NAME)
    temp_hold_user_data = []

    for user_post_data in user_info.find_all(SHREDDIT_POST, class_=GET_POST_DATA_FINDALL_CLASS):
        # Add <<post URL>>
        temp_hold_user_data.append(user_post_data["permalink"])
        # Add <<username>>
        temp_hold_user_data.append(user_post_data["author"])
        post_url_path = REDDIT_WEBPAGE_ADDRESS + user_post_data.find('a', class_='absolute inset-0').get('href')
        try:
            post_request = requests.get(url=post_url_path, headers=REQUEST_HEADERS, timeout=10)
        except requests.exceptions.Timeout:
            logger.error("TIMED OUT doing post_request")
            continue
        logger.info("Loaded posts URL: {}".format(post_url_path))
        soup_post = BeautifulSoup(post_request.text, HTML_PARSER)
        if does_post_has_restrictions(soup_post):
            continue
        post_author_profile_url = REDDIT_WEBPAGE_ADDRESS + soup_post.find('a', class_='author-name').get('href')
        try:
            author_profile_request = requests.get(url=post_author_profile_url, headers=REQUEST_HEADERS, timeout=10)
        except requests.exceptions.Timeout:
            logger.error("TIMED OUT doing post_author_profile_request")
            continue
        logger.info("Loaded post author profile URL: {}".format(post_author_profile_url))
        soup_author_profile = BeautifulSoup(author_profile_request.text, HTML_PARSER)
        cake_day = soup_author_profile.find(AUTHOR_PROFILE_FIND).get("ts")
        # Add <<user cake day>>
        temp_hold_user_data.append(str(cake_day))
        find_post_karma = soup_author_profile.find_all("div", class_="flex flex-col min-w-0")
        for karma in find_post_karma:
            try:
                if soup_author_profile.find('p',
                                            class_=AUTHOR_PROFILE_FIND_CLASS_TEXT_12).get_text(
                    strip=True) == 'Post Karma':
                    author_comment_karma = karma.find('span', {'data-testid': 'karma-number'}).get_text(strip=True)
                    # Add <<comment karma>> when text-12 in class
                    temp_hold_user_data.append(str(author_comment_karma))
                elif soup_author_profile.find('p',
                                              class_=AUTHOR_PROFILE_FIND_CLASS_TEXT_12).get_text(
                    strip=True) == 'Comment Karma':
                    author_karma = soup_author_profile.find('span', {'data-testid': 'karma-number'}).get_text(
                        strip=True)
                    # Add <<post karma>> when text-12 in class
                    temp_hold_user_data.append(str(author_karma))
                    break
            except:
                if soup_author_profile.find('p',
                                            class_=AUTHOR_PROFILE_FIND_CLASS_TEXT_14).get_text(
                    strip=True) == 'Post Karma':
                    author_comment_karma = karma.find('span', {'data-testid': 'karma-number'}).get_text(strip=True)
                    # Add <<comment karma>> when text-14 in class
                    temp_hold_user_data.append(str(author_comment_karma))
                elif soup_author_profile.find('p',
                                              class_=AUTHOR_PROFILE_FIND_CLASS_TEXT_14).get_text(
                    strip=True) == 'Comment Karma':
                    author_karma = soup_author_profile.find('span', {'data-testid': 'karma-number'}).get_text(
                        strip=True)
                    # Add <<post karma>> when text-14 in class
                    temp_hold_user_data.append(str(author_karma))
                    break
        # Add <<post date>>
        temp_hold_user_data.append(user_post_data["created-timestamp"])
        # Add <<number of comments>>
        temp_hold_user_data.append(user_post_data["comment-count"])
        # Add <<number of votes>>
        temp_hold_user_data.append(user_post_data.get("score", "N/A"))
        # Delete duplicate data
        temp_hold_user_data = list(dict.fromkeys(temp_hold_user_data))
        logger.info(NUMBER_OF_POSTS_NEEDED_TO_GET + str(number_of_posts))
        number_of_posts -= 1

        send_data_to_server(temp_hold_user_data)

        if number_of_posts == 0:
            logger.info(NUMBER_OF_POSTS_NEEDED_TO_GET + str(number_of_posts))
            return number_of_posts
        temp_hold_user_data.clear()
    return number_of_posts


def parse_command_line_arg():
    parser = argparse.ArgumentParser(description="Reddit Scraper")
    parser.add_argument("--posts", default=10, type=int, help="Number of posts to scrape")
    parser.add_argument("--category", default='top', type=str, help=f"Category of posts {CATEGOTY_COMMAND_LINE}")
    parser.add_argument("--period", default='month', type=str, help=f"Select period {PERIOD_COMMAND_LINE}")
    args = parser.parse_args()
    try:
        if args.posts <= 0:
            raise ValueError("Number of posts must be a positive integer and higher than 0 ")
        elif args.category not in CATEGOTY_COMMAND_LINE:
            raise ValueError(f"Category of post must be in {CATEGOTY_COMMAND_LINE}")
        elif args.period not in PERIOD_COMMAND_LINE:
            raise ValueError(f"Period of post must be in {PERIOD_COMMAND_LINE}")
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    number_of_posts = args.posts
    if args.category == 'top':
        main_url = f"https://www.reddit.com/r/popular/top/?t={args.period}"
    else:
        main_url = f"https://www.reddit.com/r/popular/{args.category}/"
    return number_of_posts, main_url


def main():
    number_of_posts, main_url = parse_command_line_arg()
    # If a log file is open, close it
    if os.path.isfile(LOG_FILE_NAME):
        logging.shutdown()

    delete_reddit_and_my_logfile()

    while True:
        remaining_posts_count = get_remaining_posts_num(main_url, number_of_posts)
        if not remaining_posts_count:
            sys.exit("\n Finished!!! \n")
        number_of_posts = remaining_posts_count
        next_url = get_next_url(main_url)
        if next_url is None:
            sys.exit("No more pages to scrape.")
        main_url = next_url


if __name__ == "__main__":
    main()
