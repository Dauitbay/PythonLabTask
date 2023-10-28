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


HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;\
        q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,\
            application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8,uz;q=0.7",
    "Cache-Control": "max-age=0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, \
        like Gecko) Chrome/117.0.0.0 Safari/537.36",
}
# Constants
HTML_PROCESSER = "lxml"
SHREDDIT_APP = "shreddit-app"
SHREDDIT_POST = "shreddit-post"
MAIN_URL = "https://www.reddit.com/r/popular/top/?t=month"
REDDIT_WEBPAGE_ADDRESS = "https://www.reddit.com"
SOUP_FIND_CLASS_NAME = (
    "overflow-x-hidden xs:overflow-visible v2 pt-[var(--page-y-padding)]")
GET_POST_DATA_FINDALL_CLASS = "block relative cursor-pointer bg-neutral-background focus-within:bg-neutral-background-hover hover:bg-neutral-background-hover xs:rounded-[16px] p-md my-2xs nd:visible"
LOG_FILE_NAME = "my_logfile.log"

logging.basicConfig(
    level=logging.INFO,
    filename=LOG_FILE_NAME,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger("scraper")
logger.setLevel(logging.INFO)


def unique_id():
    rand_id = uuid.uuid4().hex
    return rand_id


def delete_existing_file():
    for fname in os.listdir("."):
        if fname.startswith(("reddit-", "my_logfile")):
            os.remove(fname)


def get_current_time():
    now = datetime.now()
    generate_time = now.strftime("%Y_%m_%d_%H_%M")
    return generate_time


def write_to_file(user_data, cur_time):
    with open(f"reddit-{cur_time}.txt", "a+") as file:
        file.write("UNIQUE_ID: " + unique_id())
        joined_data = ";".join(user_data)
        file.write(joined_data)
        file.write("\n")

# Finding URL of next page and sending to get_post_data func. through main func.
def get_next_url(url: str):
    try:
        next_page_req = requests.get(url=url, headers=HEADERS, timeout=10)
        logger.info("loaded next pages url {}".format(url))
        next_page_soup = BeautifulSoup(next_page_req.text, HTML_PROCESSER)
        create_next_url = ""
        sleep(randint(1, 2))
        find_next_url = (
            next_page_soup.find(SHREDDIT_APP, class_=SOUP_FIND_CLASS_NAME)
            .find("faceplate-partial", attrs={"slot": "load-after"})
            .get("src")
        )
        create_next_url = create_next_url + (
            REDDIT_WEBPAGE_ADDRESS + str(find_next_url)
        )
    except requests.exceptions.Timeout:
        print("TIMED OUT doing request to next page")
    return create_next_url

#Gathering required data from posts
def get_post_data(posts_url: str, number_of_posts: int, file_name: str):
    try:
        result = requests.get(url=posts_url, headers=HEADERS, timeout=10)
    except requests.exceptions.Timeout:
        print("TIMED OUT doing posts_url_request")
    soup = BeautifulSoup(result.text, HTML_PROCESSER)
    user_info = soup.find(SHREDDIT_APP, class_=SOUP_FIND_CLASS_NAME)
    temp_hold_user_data = []
    for k in user_info.find_all(SHREDDIT_POST, class_=GET_POST_DATA_FINDALL_CLASS):
        temp_hold_user_data.append(" post_URL: " + k["permalink"])
        temp_hold_user_data.append(" username: " + k["author"])
        temp_hold_user_data.append(" post_date: " + k["created-timestamp"])
        temp_hold_user_data.append(" post_comment_number: " + k["comment-count"])
        temp_hold_user_data.append(" number_of_votes: " + k["score"])
        temp_hold_user_data.append(" post_type: " + k["post-type"])
        # Getting post URL and sending request there:
        k = f"https://www.reddit.com{k.find('a', class_ ='absolute inset-0').get('href')}"
        try:
            post_request = requests.get(url=k, headers=HEADERS, timeout=10)
        except requests.exceptions.Timeout:
            print("TIMED OUT doing post_request")
        logger.info("loaded post url {}".format(k))
        soup_post = BeautifulSoup(post_request.text, HTML_PROCESSER)
        # IF web page has age restriction to some contents
        if_age_limit = soup_post.find("a", class_="author-name")
        if if_age_limit is None:
            temp_hold_user_data.clear()
            continue
        # Getting  post's author's URL and sending request there:
        post_author_profile_url = f"https://www.reddit.com{soup_post.find('a', class_ = 'author-name').get('href')}"
        try:
            author_profile_request = requests.get(
                url=post_author_profile_url, headers=HEADERS, timeout=10
            )
        except requests.exceptions.Timeout:
            print("TIMED OUT doing post_author_profile_request")
        soup_author_profile = BeautifulSoup(author_profile_request.text, HTML_PROCESSER)
        check_for_blocked_account = soup_author_profile.find("faceplate-date")
        #If user is BLOCKED by web site or DELETED
        if check_for_blocked_account is None:
            temp_hold_user_data.clear()
            continue
        # Getting "user_cake_day","post_karma" and "comment_karma" from post's authors profile:
        cake_day = check_for_blocked_account.get("ts")
        temp_hold_user_data.append(" user_cake_day: " + str(cake_day))
        author_post_karma = soup_author_profile.find(
            "faceplate-number", class_="font-semibold text-14"
        ).get("number")
        temp_hold_user_data.append(" post_karma: " + author_post_karma)
        find_post_karma = soup_author_profile.find_all(
            "div", class_="flex flex-col min-w-0"
        )
        for karma in find_post_karma:
            author_comment_karma = karma.find(
                "faceplate-number", class_="font-semibold text-14"
            ).get("number")
            temp_hold_user_data.append(" comment_karma: " + author_comment_karma)
            break
        temp_hold_user_data = list(dict.fromkeys(temp_hold_user_data))
        print(f"Number of posts needed to get {number_of_posts}....")
        number_of_posts -= 1
        write_to_file(temp_hold_user_data, file_name)

        # Exiting function after collecting required amount of data:
        if number_of_posts == 0:
            print(f"Number of posts needed to get {number_of_posts}")
            return number_of_posts
        temp_hold_user_data.clear()
    return number_of_posts


def main():
    #If log file is open close it
    if os.path.isfile(LOG_FILE_NAME):
        logging.shutdown()

    delete_existing_file()
    start_time = get_current_time()
    main_url = MAIN_URL
    # Setting number_of_posts to GET :
    number_of_posts = 100
    while True:
        returned_number_of_posts = get_post_data(
            main_url, number_of_posts, str(start_time)
        )
        if not returned_number_of_posts:
            sys.exit("Finished!!!")
        number_of_posts = returned_number_of_posts
        next_url = get_next_url(main_url)
        main_url = next_url


if __name__ == "__main__":
    main()
