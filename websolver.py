#! /usr/bin/env python3
# coding: utf-8

import sqlite3
import requests
import re
import lxml
from bs4 import BeautifulSoup

store=''
app_stores={'kuan':'https://www.coolapk.com/apk','wandoujia':'https://www.wandoujia.com/apps'}
#kuan also has a web:https://www.coolapk.com/game
class crawler():
    def __init__(self,store):
        self.url = app_stores[store]
        self.store = store
    def get_links(self):
        if self.store=='kuan':
            payload={'p':1}
            res = requests.post(self.url,params=payload)
            markup = res.text
            # print(markup)
            soup = BeautifulSoup(markup,"lxml")
            # print(soup)
            soup = soup.find('div','app_left_list')
            # print(soup)
            apks = soup.find_all('a')
            for apk in apks[:10]:
                print(apk.get('href'))
                #add to sqlite3
            lastpage_href = apks[-1].get('href')
            reg = re.compile(r"=\d+")
            Maxpage = int(reg.search(lastpage_href)[0][1:])
            # print(Maxpage)
            
            for i in range(2,Maxpage+1):
                payload={'p':i}
                res = requests.post(self.url,params=payload)
                markup = res.text
                # print(markup)
                soup = BeautifulSoup(markup,"lxml")
                # print(soup)
                soup = soup.find('div','app_left_list')
                # print(soup)
                apks = soup.find_all('a')
                for apk in apks[:10]:
                    href = apk.get('href')
                    if href.startswith(r'/apk?p='):
                        break
                    print(apk.get('href'))
                    #add to sqlite3

                
        else:
            print('Cannot found target appstore:%s'%store)
            exit(1)
    
def main():
    craw = crawler('kuan')
    craw.get_links()

if __name__ == '__main__':
    main()