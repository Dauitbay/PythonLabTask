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

and save them to file by giving unique_ID to a file with name reddit-YYYYMMDDHHmm.txt
Every time we run code it will delite previus reddit-YYYYMMDDHHmm.txt

## Setup required to this project
Install the dependencies:

$ python -m pip install beautifulsoup4

$ python -m pip install requests

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
Main file is reddit_main.py 
Scraping web page is reddit.com which is dynamic web page(loades content when user scrools).

1-step: In main function we can give number of posts we need in varible called: number_of_posts

2-step: It will get requred data from first loaded posts which are located in CSS: shreddit-app by class:class="overflow-x-hidden xs:overflow-visible v2 pt-[var(--page-y-padding)]"

3-step: It will get url to next page which is located in CSS: faceplate-partial slot="load-after" where url located in [src="/svc/shreddit/feeds/popular-feed......] and will continue getting data we need.

4-step: While getting data we will write them to file with unique ID which is created with date and time we started code. Also we create log file to check saving them to file called: my_logfile.log.

5- step: Every time we RUN our code it will delite existing log and saved post files from previus run.


## Authors and acknowledgment
I am very gratiful to [https://gitlab.com/alexey.bogushevich] and [https://gitlab.com/MaksimShelehItechArt] (Ventionteams developers)  for giving me task to learn more  and helping to finish it by correcting me when needed. Also Taxir's advices also helped me during developing stage.

Also PythonTodays lessons were helpful: https://www.youtube.com/@PythonToday

## Contributing
If you have a suggestion that would make this better, please leave your comments.

## Support
Contact me if you have questions.

LinkedIn: www.linkedin.com/in/dawitsarsenbaev

Email: dawitsarsenbaev@gmail.com

## Project status
Needs review
