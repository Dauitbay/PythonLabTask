"""main_reddit.py does request to reddit.com (MONTH TOP posts) to get:

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
    And saves them in reddit-YYYYMMDDHHMM.txt giving UNIQUE_ID
    to every USER DATA.
    AROUND 8-9 minutes required to gather 100 user data.
"""
from datetime import datetime
from time import sleep
from random import randint
import os
import os.path
import logging
import uuid
import sys
import requests
from bs4 import BeautifulSoup


# Constants
REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;\
        q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,\
            application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8,uz;q=0.7",
    "Cache-Control": "max-age=0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, \
        like Gecko) Chrome/117.0.0.0 Safari/537.36",
}
HTML_PARSER = "lxml"
SHREDDIT_APP = "shreddit-app"
SHREDDIT_POST = "shreddit-post"
MAIN_URL = "https://www.reddit.com/r/popular/top/?t=month"
REDDIT_WEBPAGE_ADDRESS = "https://www.reddit.com"
SOUP_FIND_CLASS_NAME = (
    "overflow-x-hidden xs:overflow-visible v2 pt-[var(--page-y-padding)]")
GET_POST_DATA_FINDALL_CLASS = "block relative cursor-pointer bg-neutral-background focus-within:bg-neutral-background-hover hover:bg-neutral-background-hover xs:rounded-[16px] p-md my-2xs nd:visible"
LOG_FILE_NAME = "my_logfile.log"
NUMBER_OF_POSTS_NEEDED_TO_GET = "Number of posts needed to get --> "


logging.basicConfig(
    level=logging.INFO,
    filename=LOG_FILE_NAME,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger("scraper")
logger.setLevel(logging.INFO)

def generate_unique_id():
    unique_id = uuid.uuid1().hex
    return unique_id[:32]


def delete_reddit_and_mylog_file():
    for fname in os.listdir("."):
        if fname.startswith(("reddit-", "my_logfile")):
            os.remove(fname)


def get_current_time():
    now = datetime.now()
    return now.strftime("%Y_%m_%d_%H_%M")


def write_to_file(user_data, cur_time):
    with open(f"reddit-{cur_time}.txt", "a+") as file:
        file.write("UNIQUE_ID: " + generate_unique_id())
        joined_data = ";".join(user_data)
        file.write(joined_data)
        file.write("\n")

# Finding URL of next page and sending to get_remaining_posts_num func. through main func.
def get_next_url(url: str):
    try:
        next_page_req = requests.get(url=url, headers=REQUEST_HEADERS, timeout=10)
        logger.info("loaded next pages url {}".format(url))
        next_page_soup = BeautifulSoup(next_page_req.text, HTML_PARSER)
        create_next_url = ""
        sleep(randint(0, 1))
        find_next_url = (
            next_page_soup.find(SHREDDIT_APP, class_=SOUP_FIND_CLASS_NAME)
            .find("faceplate-partial", attrs={"slot": "load-after"})
            .get("src")
        )
        create_next_url = create_next_url + (
            REDDIT_WEBPAGE_ADDRESS + str(find_next_url)
        )
    except requests.exceptions.Timeout:
        logger.info("TIMED OUT doing request to next page")
    return create_next_url


def does_post_has_restrictions(soup: BeautifulSoup):
    author_link = soup.find('a', class_='author-name')
    if author_link is None:
        logger.info("Age restriction. Could not access the author's profile.")
        return False
    post_author_profile_url = REDDIT_WEBPAGE_ADDRESS + author_link.get('href')
    try:
        author_profile_request = requests.get(url=post_author_profile_url, headers=REQUEST_HEADERS, timeout=10)
    except requests.exceptions.Timeout:
        logger.error("TIMED OUT doing post_author_profile_request")
        return False
    soup_author_profile = BeautifulSoup(author_profile_request.text, HTML_PARSER)
    faceplate_date = soup_author_profile.find("faceplate-date")
    if faceplate_date is None:
        logger.info("Author is BLOCKED. Could not access the author's profile.")
        return False
    return True


#Gathering required data from posts and returning num of posts
def get_remaining_posts_num(posts_url: str, number_of_posts: int, file_name: str):
    try:
        result = requests.get(url=posts_url, headers=REQUEST_HEADERS, timeout=10)
    except requests.exceptions.Timeout:
        logger.error("TIMED OUT doing posts_url_request")
        return number_of_posts

    soup = BeautifulSoup(result.text, HTML_PARSER)
    user_info = soup.find(SHREDDIT_APP, class_=SOUP_FIND_CLASS_NAME)
    temp_hold_user_data = []

    for user_post_data in user_info.find_all(SHREDDIT_POST, class_=GET_POST_DATA_FINDALL_CLASS):
        temp_hold_user_data.append(" post_URL: " + user_post_data["permalink"])
        temp_hold_user_data.append(" username: " + user_post_data["author"])
        temp_hold_user_data.append(" post_date: " + user_post_data["created-timestamp"])
        temp_hold_user_data.append(" post_comment_number: " + user_post_data["comment-count"])
        temp_hold_user_data.append(" number_of_votes: " + user_post_data["score"])
        temp_hold_user_data.append(" post_type: " + user_post_data["post-type"])
        post_url_path = REDDIT_WEBPAGE_ADDRESS + user_post_data.find('a', class_='absolute inset-0').get('href')
        try:
            post_request = requests.get(url=post_url_path, headers=REQUEST_HEADERS, timeout=10)
        except requests.exceptions.Timeout:
            logger.error("TIMED OUT doing post_request")
            continue
        logger.info("Loaded post URL: {}".format(post_url_path))
        soup_post = BeautifulSoup(post_request.text, HTML_PARSER)

        if not does_post_has_restrictions(soup_post):
            continue

        post_author_profile_url = REDDIT_WEBPAGE_ADDRESS + soup_post.find('a', class_='author-name').get('href')
        try:
            author_profile_request = requests.get(url=post_author_profile_url, headers=REQUEST_HEADERS, timeout=10)
        except requests.exceptions.Timeout:
            logger.error("TIMED OUT doing post_author_profile_request")
            continue
        logger.info("Loaded post author profile URL: {}".format(post_author_profile_url))
        soup_author_profile = BeautifulSoup(author_profile_request.text, HTML_PARSER)

        if does_post_has_restrictions(soup_author_profile):
            continue

        # Getting "user_cake_day","post_karma" and "comment_karma" from post's author's profile:
        cake_day = soup_author_profile.find("faceplate-date").get("ts")
        temp_hold_user_data.append(" user_cake_day: " + str(cake_day))
        author_post_karma = soup_author_profile.find("faceplate-number", class_="font-semibold text-14").get("number")
        temp_hold_user_data.append(" post_karma: " + author_post_karma)
        find_post_karma = soup_author_profile.find_all("div", class_="flex flex-col min-w-0")
        for karma in find_post_karma:
            author_comment_karma = karma.find("faceplate-number", class_="font-semibold text-14").get("number")
            temp_hold_user_data.append(" comment_karma: " + author_comment_karma)
            break
        temp_hold_user_data = list(dict.fromkeys(temp_hold_user_data))
        logger.info(NUMBER_OF_POSTS_NEEDED_TO_GET  + str(number_of_posts))
        number_of_posts -= 1
        write_to_file(temp_hold_user_data, file_name)

        # Exiting function after collecting the required amount of data:
        if number_of_posts == 0:
            logger.info(NUMBER_OF_POSTS_NEEDED_TO_GET  + str(number_of_posts))
            return number_of_posts
        temp_hold_user_data.clear()

    return number_of_posts


def main():
    # If a log file is open, close it
    if os.path.isfile(LOG_FILE_NAME):
        logging.shutdown()

    delete_reddit_and_mylog_file()
    start_time = get_current_time()
    main_url = MAIN_URL
    number_of_posts = 100
    while True:
        get_number_of_posts = get_remaining_posts_num(main_url, number_of_posts, start_time)
        if not get_number_of_posts:
            sys.exit("Finished!!!")
        number_of_posts = get_number_of_posts
        next_url = get_next_url(main_url)

        if next_url is None:
            sys.exit("No more pages to scrape.")
        main_url = next_url


if __name__ == "__main__":
    main()
