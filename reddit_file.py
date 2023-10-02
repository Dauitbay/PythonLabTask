
from bs4 import BeautifulSoup
import requests
# import html5lib

url = "https://www.reddit.com/r/popular/top/?t=month"

result = requests.get(url)
if result.status_code != 200:
    print("Failed to connect")
    exit()
# soup = BeautifulSoup(result.text, "html.parser")
soup = BeautifulSoup(result.text, "html5lib")

# elements = soup.find_all("shreddit-feed", class_ = "nd:visible")
elements = soup.find_all("shreddit-feed", class_ = "nd:visible")

# all_info = []
# for el in elements:
#     all_info.append(el.find("span", class_ = "relative"))
# print(all_info)



# print(elements)
# for elem in elements:

#     post_data = []
#     post_data.append(elem.find())
#     post_data.append(elem['post-title'])
#     post_data.append(elem['author'])
#     post_data.append(elem['id'])
#     post_data.append(elem['subreddit-prefixed-name'][2:])
#     post_data.append(elem['permalink'])
#     post_data.append(elem['created-timestamp'])
#     post_data.append(elem['score'])
#     post_data.append(elem['comment-count'])
# print(post_data)

  
    # next_button = soup.find("span", class_="next-button")
    # next_page_link = next_button.find("a").attrs['href']
    # time.sleep(2)
    # page = requests.get(next_page_link, headers=headers)
    # soup = BeautifulSoup(page.text, 'html.parser')