
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import os

url = "https://www.reddit.com/r/popular/top/?t=month"

#Deleting existing .txt file: 
def delete_existing_file():
    for fname in os.listdir('.'):
        if fname.endswith('.txt'):
            os.remove(fname)
            break

#Getting current time:

#Getting data from reddit.com
def get_data(url_reddit):

    result = requests.get(url_reddit)

    #Checking for connection:
    if result.status_code != 200:
        print("Failed to connect")
        exit()

    # soup = BeautifulSoup(result.text, "html.parser")
    # user_info = soup.find('shreddit-feed', class_ = "nd:visible")   

    # for i in user_info.find_all('shreddit-post', class_ = 'block relative cursor-pointer bg-neutral-background focus-within:bg-neutral-background-hover hover:bg-neutral-background-hover xs:rounded-[16px] p-md my-2xs nd:visible'):
    #     print(i['id'])
    #     print(i['permalink'])
    #     print(i['content-href'])

def get_current_time():
    now = datetime.now()
    generate_time = now.strftime("%Y_%m_%d_%H_%M")
    return generate_time

#Writing data to a file current_time.txt:
def write_to_file(hold_data, cur_time):
    f = open(f"{cur_time}.txt", "w")
    f.write(hold_data)
    f.write("\n")

#Calling functions:
delete_existing_file()
current_time = get_current_time()
res = get_data(url)
write_to_file(res, current_time)
