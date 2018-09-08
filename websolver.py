#! /usr/bin/env python3
# coding: utf-8

import sqlite3
import requests
from bs4 import BeautifulSoup

app_stores={'kuan':'https://www.coolapk.com/apk','wandoujia':'https://www.wandoujia.com/apps'}

class crawler(store):
    def __init__(self,store):
        self.url = app_stores[store]
    def get_links(store):
        if store=='kuan':
            re = requests.post(url)
        else:
            print('Cannot found target appstore:%s'%store)
            exit(1)
        