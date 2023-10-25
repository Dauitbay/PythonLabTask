
from bs4 import BeautifulSoup
from datetime import datetime
from random import randint
from time import sleep
import os, os.path 
import requests
import logging
import uuid

# Create and configure logger
logging.basicConfig(level=logging.INFO, filename='my_logfile.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
# Creating an object:
logger = logging.getLogger('scraper')
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)

# Creating varible to provide authentication for requests:
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"en-GB,en-US;q=0.9,en;q=0.8,uz;q=0.7",
    "Cache-Control":"max-age=0", 
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# Create random unique ID:
def unique_id():
    # Make a random UUID and converting it to a 32-character hexadecimal string
    rand_id = uuid.uuid4().hex
    return rand_id

#Deleting existing .txt and .log files before collecting data: 
def delete_existing_file():
    for fname in os.listdir('.'):
        if fname.startswith(('reddit-', 'my_logfile')): 
            os.remove(fname)

#Getting current time to name file with users data in it:
def get_current_time():
    now = datetime.now()
    generate_time = now.strftime("%Y_%m_%d_%H_%M")
    return generate_time

#Write user data to a file reddit-YYYYMMDDHHmm.txt (Y-year; M-month; D-day; H-hour; m-minute):
def write_to_file(user_data, cur_time):
    with open(f"reddit-{cur_time}.txt", "a+") as file:
        file.write('UNIQUE_ID: ' + unique_id())
        a = ";".join(user_data)
        file.write(a)
        file.write("\n")

def get_next_url(url):

    try:
        result = requests.get(url=url, headers=HEADERS)
        logger.info('loaded next pages url {}'.format(url))
        soup_driver = BeautifulSoup(result.text, "lxml")  
        next_url_hold = ""
        sleep(randint(1, 2))
        next_url= soup_driver.find('shreddit-app', class_ = "overflow-x-hidden xs:overflow-visible v2 pt-[var(--page-y-padding)]").find("faceplate-partial", attrs={"slot":"load-after"}).get("src")
        next_url_hold = next_url_hold + ("https://www.reddit.com" + str(next_url))

    except Exception as _ex:
       print("_ex")
           
    finally:
        return next_url_hold

def get_post_data(url_1:str, number_of_posts:int, file_name: str):

    result = requests.get(url=url_1, headers=HEADERS)
    soup = BeautifulSoup(result.text, "lxml")    
    user_info = soup.find('shreddit-app', class_ = "overflow-x-hidden xs:overflow-visible v2 pt-[var(--page-y-padding)]")

    hold_d = []
    for k in user_info.find_all('shreddit-post', class_ = "block relative cursor-pointer bg-neutral-background focus-within:bg-neutral-background-hover hover:bg-neutral-background-hover xs:rounded-[16px] p-md my-2xs nd:visible"):
        hold_d.append(' post_URL: ' + k['permalink'])
        hold_d.append(' username: ' + k['author'])
        hold_d.append(' post_date: ' + k['created-timestamp'])
        hold_d.append(' post_comment_number: ' + k['comment-count'])
        hold_d.append(' number_of_votes: ' + k['score'])
        hold_d.append(' post_type: ' + k['post-type'])

        # Getting post URL and sending request there:
        k = f"https://www.reddit.com{k.find('a', class_ = 'absolute inset-0').get('href')}"
        post_request = requests.get(url=k, headers=HEADERS)
        #Logging info:
        logger.info('loaded post url {}'.format(k))
        soup_post = BeautifulSoup(post_request.text, "lxml")
        check_for_mature_content = soup_post.find('a', class_ = 'author-name')
        if check_for_mature_content == None:
             hold_d.clear()
             continue
        
        # Getting  post's author's URL and sending request there:
        post_author_profile_url = f"https://www.reddit.com{soup_post.find('a', class_ = 'author-name').get('href')}"       
        author_profile_request = requests.get(url=post_author_profile_url, headers=HEADERS)
        soup_author_profile = BeautifulSoup(author_profile_request.text, "lxml")
        check_for_blocked_account = soup_author_profile.find("faceplate-date")
        if check_for_blocked_account == None:
             hold_d.clear()
             continue 
        
        #Getting "user_cake_day","post_karma" and "comment_karma" from post's authors profile:
        cake_day = check_for_blocked_account.get('ts')
        hold_d.append(' user_cake_day: ' + str(cake_day))
        a_post_karma = soup_author_profile.find('faceplate-number', class_ = 'font-semibold text-14').get('number')
        hold_d.append(' post_karma: ' + a_post_karma)
        post_karma = soup_author_profile.find_all('div', class_ = 'flex flex-col min-w-0')  
        for i in post_karma:
            a_comment_karma = i.find('faceplate-number', class_ = 'font-semibold text-14').get('number')
            hold_d.append(' comment_karma: ' + a_comment_karma)
            break
        
        hold_d = list(dict.fromkeys(hold_d))
        print(f"Number of posts needed to get {number_of_posts}....")
        number_of_posts -= 1
        write_to_file(hold_d, file_name)

        #Exiting function after collecting required amount of data: 
        if number_of_posts == 0:
            print(f"Number of posts needed to get {number_of_posts}....")
            print("Finished collecting data !!!")
            return number_of_posts
        hold_d.clear()
    return number_of_posts
    
def main():
    if os.path.isfile('my_logfile.log'):
        logging.shutdown()

    delete_existing_file()
    start_time = get_current_time()
    main_url = "https://www.reddit.com/r/popular/top/?t=month"

    # Setting number_of_posts to GET from reddit.com:
    number_of_posts = 10
    while True:
        returned_number_of_posts = get_post_data(main_url, number_of_posts, str(start_time))
        if not returned_number_of_posts:
            exit()
        number_of_posts = returned_number_of_posts
        n_url = get_next_url(main_url)
        main_url = n_url

if __name__ == '__main__':
    main()
