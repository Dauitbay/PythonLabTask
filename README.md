# PythonLabTask

## Project Description
This project scraps web page reddit.com using beautifulsoup4 and requests.

From this web page we get:

-post URL;

-username;

-user karma;

-user cake day;

-post karma;

-comment karma;

-post date;

-number of comments;

-number of votes;

-post category

and save them to file by giving unique_ID to users we collect from web page with file name reddit-YYYYMMDDHHmm.txt .
Every time we run code it will delete previus reddit-YYYYMMDDHHmm.txt and my_logfile.log files.

## Setup required to this project
Install the dependencies:

Create virtual env(link to example of commands):
https://docs.python.org/3/library/venv.html

Command to install libs from requirements.txt file:
Use the pip install -r requirements.txt command to install all of the Python modules and packages listed in requirements.txt file.

To deactivate your virtual environment, simply run the following code in the terminal:
deactivate

## Requred imports

from bs4 import BeautifulSoup

from datetime import datetime

from random import randint

from time import sleep

import os, os.path 

import requests

import logging

import uuid

## How code works
Main file is main_reddit.py 
Scraping web page is reddit.com which is dynamic web page(loades content when user scrools).

1-step: In main function we can give number of posts we need in varible called: number_of_posts

2-step: It will get requred data from first loaded posts which are located in CSS: shreddit-app by class:class="overflow-x-hidden xs:overflow-visible v2 pt-[var(--page-y-padding)]"

3-step: It will get url to next page which is located in CSS: faceplate-partial slot="load-after" where url located in [src="/svc/shreddit/feeds/popular-feed......] and will continue getting data we need.

4-step: While getting users data we will write them to file reddit-YYYYMMDDHHmm.txt with unique ID. Also we create log file and saving logging info to file called: my_logfile.log.

5- step: Every time we RUN our code it will delete existing log and saved reddit-YYYYMMDDHHmm.txt from previus run.
