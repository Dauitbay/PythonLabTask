
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import uuid
import os
import json

url = "https://www.reddit.com/r/popular/top/?t=month"

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
    # for i in hold_data:
    f.write(a)
    f.write("\n")
    # f.write(i)

#Getting data from reddit.com
def get_data(url_reddit):

    result = requests.get(url_reddit)

    #Checking for connection:
    if result.status_code != 200:
        print("Failed to connect")
        exit()

    soup = BeautifulSoup(result.text, "html.parser")
    user_info = soup.find('shreddit-feed', class_ = "nd:visible")   
    for k in user_info.find_all('shreddit-post', class_ = "block relative cursor-pointer bg-neutral-background focus-within:bg-neutral-background-hover hover:bg-neutral-background-hover xs:rounded-[16px] p-md my-2xs nd:visible"):
        hold_d = []
        hold_d.append(' post URL: ' + k['permalink'])
        hold_d.append(' username: ' + k['author'])
        hold_d.append(' subreddit-prefixed-name: ' + k['subreddit-prefixed-name'])
        hold_d.append(' post karma: ' + k['score'])
        hold_d.append(' comment karma: ' + k['comment-count'])
        hold_d.append(' post date: ' + k['created-timestamp'])
        hold_d.append(' post type:' + k['post-type'])
        write_to_file(hold_d, get_current_time())
        hold_d.clear()

#Calling functions:
delete_existing_file()
current_time = get_current_time()
get_data(url)
