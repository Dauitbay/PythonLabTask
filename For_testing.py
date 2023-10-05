from datetime import datetime
import os


# for fname in os.listdir('.'):
#     if fname.endswith('.txt'):
#         os.remove(fname)
#         print("True")
#         break
# else:
#     print("Hello")

def get_data():
    return "Hello return after delete"

def get_current_time():
    now = datetime.now()
    generate_time = now.strftime("%Y_%m_%d_%H_%M")
    return generate_time

#Writing data to a file current_time.txt:
def delete_existing_file():
    for fname in os.listdir('.'):
        if fname.endswith('.txt') or fname.startswith(current_time):
            os.remove(fname)
            break

def write_to_file(hold_data, cur_time):
    f = open(f"{cur_time}.txt", "w")
    # for data in soup.select('[itemprop=itemListElement] [itemprop=url]'):
        # data = data.get('content')
    f.write(hold_data)
    f.write("\n")
    
current_time = get_current_time()
res = get_data()

delete_existing_file()
write_to_file(res, current_time)


       # elements = soup.find_all("shreddit-feed", class_ = "nd:visible")
    # elements = soup.find_all("shreddit-feed", attrs={'class': 'nd:visible'})
    # print(elements)

# for elem in elements:
#     post_data = []
#     post_data.append(elem['post-title'])
#     post_data.append(elem['author'])
#     post_data.append(elem['id'])
#     post_data.append(elem['subreddit-prefixed-name'][2:])
#     post_data.append(elem['permalink'])
#     post_data.append(elem['created-timestamp'])
#     post_data.append(elem['score'])
#     post_data.append(elem['comment-count'])
# print(post_data)

'''
def get_url_for_parsing(url):

    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        parsed_url = soup.find('a')['href']
        return parsed_url
    return None

url = 'https://www.example.com'
parsed_url = get_url_for_parsing(url)

if parsed_url:
    print('URL for parsing:', parsed_url)
else:
    print('Failed to retrieve URL for parsing.')
'''

# for i in range(0, 100, 50):
#     URL= "https://reelgood.com/movies/source/netflix?offset=" + str(i)
#     result = requests.get(URL)
#     soup = BeautifulSoup(result.content, "html.parser")
