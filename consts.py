"""
Here are constants for main_reddit_parser.py file which scraps web page reddit.com using Beautifulsoup

"""
import http.client
import datetime
import os
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
LOG_FILE_NAME = "my_logfile.log"
NUMBER_OF_POSTS_NEEDED_TO_GET = "Number of posts needed to get --> "
CATEGOTY_COMMAND_LINE = ['best', 'hot', 'new', 'top', 'rising']
PERIOD_COMMAND_LINE = ['hour', 'day', 'week', 'month', 'year', 'all']

# Below CONSTANTS may change in reddit.com
AUTHOR_PROFILE_FIND = "faceplate-tracker"
SHREDDIT_APP = "shreddit-app"
SHREDDIT_POST = "shreddit-post"
REDDIT_WEBPAGE_ADDRESS = "https://www.reddit.com"
SOUP_FIND_CLASS_NAME = (
    "overflow-x-hidden xs:overflow-visible v2 pt-[var(--page-y-padding)]")
GET_POST_DATA_FINDALL_CLASS = "block relative cursor-pointer bg-neutral-background focus-within:bg-neutral-background-hover hover:bg-neutral-background-hover xs:rounded-[16px] px-md py-2xs my-2xs nd:visible"

# Localhost constants
connect = http.client.HTTPConnection('localhost', 8087, timeout=10)
server_headers = {'Content-type': 'application/json'}
PROG_START_TIME = datetime.datetime.now().strftime("%Y%m%d")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATCHING_FILES = [f for f in os.listdir(BASE_DIR) if f.startswith("reddit-")]
REDDIT_FILENAME = os.path.join(BASE_DIR, MATCHING_FILES[0]) if MATCHING_FILES else None