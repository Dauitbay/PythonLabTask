
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import uuid
import os

#Giving UNIQUE_ID:
def unique_id():
    # Make a random UUID and converting it to a 32-character hexadecimal string
    rand_id = uuid.uuid4().hex
    return rand_id
    
#Deleting existing .txt file: 
def delete_existing_file():
    for fname in os.listdir('.'):
        if fname.endswith('.txt'):
            os.remove(fname)
            break
        
#Getting current time:
def get_current_time():
    now = datetime.now()
    generate_time = now.strftime("%Y_%m_%d_%H_%M")
    return generate_time

#Writing data to a file:
def write_to_file(hold_data, cur_time):
    f = open(f"{cur_time}.txt", "a")
    f.write('UNIQUE_ID: ' + unique_id())
    a = ";".join(hold_data)
    f.write(a)
    f.write("\n")

#Getting data from reddit.com
def get_data(url):

    #Checking for connection:
    def url_connection_check(check, url_name: str):
        if check.status_code != 200:
            print(f"Failed to connect" + url_name)
            exit()

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"en-GB,en-US;q=0.9,en;q=0.8,uz;q=0.7",
        "Cache-Control":"max-age=0", 
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    
    req = requests.get(url=url, headers=headers)
    url_connection_check(req, str("main url"))

    soup = BeautifulSoup(req.text, "lxml")
    user_info = soup.find('shreddit-feed', class_ = "nd:visible")   
    hold_d = []
    for k in user_info.find_all('shreddit-post', class_ = "block relative cursor-pointer bg-neutral-background focus-within:bg-neutral-background-hover hover:bg-neutral-background-hover xs:rounded-[16px] p-md my-2xs nd:visible"):
        hold_d.append(' post_URL: ' + k['permalink'])
        hold_d.append(' username: ' + k['author'])
        hold_d.append(' post_date: ' + k['created-timestamp'])
        hold_d.append(' post_comment_number: ' + k['comment-count'])
        hold_d.append(' number_of_votes: ' + k['score'])
        hold_d.append(' post_type: ' + k['post-type'])
        # hold_d.append(' subreddit-prefixed-name: ' + k['subreddit-prefixed-name'])

        k = f"https://www.reddit.com{k.find('a', class_ = 'absolute inset-0').get('href')}"
        post_request = requests.get(url=k, headers=headers)
        url_connection_check(post_request, str(post_request))

        soup_post = BeautifulSoup(post_request.text, "lxml")
        post_author_profile_url = f"https://www.reddit.com{soup_post.find('a', class_ = 'author-name').get('href')}"       
        author_profile_request = requests.get(url=post_author_profile_url, headers=headers)
        url_connection_check(author_profile_request, str(author_profile_request))

        soup_author_profile = BeautifulSoup(author_profile_request.text, "lxml")
        cake_day = soup_author_profile.find("faceplate-date").get('ts')
        hold_d.append(' user_cake_day: ' + cake_day)

        a_post_karma = soup_author_profile.find('faceplate-number', class_ = 'font-semibold text-14').get('number')
        hold_d.append(' post_karma: ' + a_post_karma)

        post_karma = soup_author_profile.find_all('div', class_ = 'flex flex-col min-w-0')  
        for i in post_karma:
            a_comment_karma = i.find('faceplate-number', class_ = 'font-semibold text-14').get('number')
            hold_d.append(' comment_karma: ' + a_comment_karma)
            break

        hold_d = list(dict.fromkeys(hold_d))
        write_to_file(hold_d, get_current_time())
        hold_d.clear()

#Calling functions in main function:
def main():
    delete_existing_file()
    get_current_time()
    get_data("https://www.reddit.com/r/popular/top/?t=month")

if __name__ == '__main__':
    main()

