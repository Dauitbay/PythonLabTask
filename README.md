# PythonLabTask

## Project Description
This project scraps web page reddit.com using beautifulsoup4 and requests.

From this web page we get:

 - post URL;
 - username;
 - user karma;
 - user cake day;
 - post karma;
 - comment karma;
 - post date;
 - number of comments;
 - number of votes;

and save them to file by giving unique_ID to users we collect from web page with file name ***reddit-YYYYMMDDHHmm.txt***.
Every time we run code it will delete previus ***reddit-YYYYMMDDHHmm.txt*** and ***my_logfile.log*** files.

We also can use command-line interface like:
***python main_reddit.py --posts 100 --category top --period month***

- In --posts : Here we can give number of posts we want to get.
- In --category : Here we can give category of post from choosing ---> best, hot, new, top, rising.
- In --period : Here we can give period of post if we choose "top" from category (Only in top we have options for period) ---> hour, day, week, month, year, all. 

## Setup required to this project
Install the dependencies:

Create virtual env(link to example of commands):
https://docs.python.org/3/library/venv.html

Command to install libs from requirements.txt file:
Use the ***pip install -r requirements.txt*** command to install all of the Python modules and packages listed in requirements.prod.txt file.

To deactivate your virtual environment, simply run the following code in the terminal:
deactivate


## How code works
Main file is main_reddit.py 
Scraping web page is reddit.com which is dynamic web page(loades content when user scrools).

***1-step:*** In main function we can give number of posts we need in varible called: number_of_posts

***2-step:*** It will get requred data from first loaded posts (just 3 posts in default and it will)

***3-step:*** It will get url to next page in function ***get_next_url*** and will send it to ***get_remaining_posts_num*** through main function and will continue getting data we need.

***4-step:*** While collecting post and user data we can face restrictions from web page. To handle restrictions we check for them in ***does_post_has_restrictions*** function. If we had restrictions we skip that post and save report in my_logfile.log to review if nessary.

***5-step:*** While getting users data we will write them to file reddit-YYYYMMDDHHmm.txt with unique ID. Also we create log file and saving logging info to file called: my_logfile.log.

***6- step:*** Every time we RUN our code it will delete existing log and saved reddit-YYYYMMDDHHmm.txt from previus run.
