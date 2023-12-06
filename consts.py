"""
Here are constants for main_reddit.py file which scraps web page reddit.com using Beautifulsoup

"""
import http.client
import datetime
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
REDDIT_WEBPAGE_ADDRESS = "https://www.reddit.com"
SOUP_FIND_CLASS_NAME = (
    "overflow-x-hidden xs:overflow-visible v2 pt-[var(--page-y-padding)]")
GET_POST_DATA_FINDALL_CLASS = "block relative cursor-pointer bg-neutral-background focus-within:bg-neutral-background-hover hover:bg-neutral-background-hover xs:rounded-[16px] p-md my-2xs nd:visible"
LOG_FILE_NAME = "my_logfile.log"
NUMBER_OF_POSTS_NEEDED_TO_GET = "Number of posts needed to get --> "
CATEGOTY_COMMAND_LINE = ['best', 'hot', 'new', 'top', 'rising']
PERIOD_COMMAND_LINE = ['hour', 'day', 'week', 'month', 'year', 'all']
# Below CONSTANTS may change in reddit.com
AUTHOR_PROFILE_FIND_CLASS_TEXT_12 = "m-0 text-neutral-content-weak text-12 whitespace-nowrap truncate"
AUTHOR_PROFILE_FIND_CLASS_TEXT_14 = "m-0 text-neutral-content-strong text-14 font-semibold whitespace-nowrap"
AUTHOR_PROFILE_FIND = "faceplate-tracker" 

conn = http.client.HTTPConnection('localhost', 8087, timeout=10)
server_headers = {'Content-type': 'application/json'}

# localserver_8087_for_reddit
PROG_START_TIME = datetime.datetime.now().strftime("%Y%m%d")