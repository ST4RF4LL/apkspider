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
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        headers={"User-Agent":user_agent}
        if self.store=='kuan':
            payload={'p':1}
            res = requests.post(self.url,params=payload,headers=headers)
            markup = res.text
            # print(markup)
            soup = BeautifulSoup(markup,"lxml")
            # print(soup)
            soup = soup.find('div','app_left_list')
            # print(soup)
            apks = soup.find_all('a')
            print('solving the %s:page:%s'%(self.store,1))

            file = open('./downlist.'+self.store,'a')

            for apk in apks[:10]:
                # print(apk.get('href'))
                href = apk.get('href')
                file.write('https://www.coolapk.com'+href+'\n')
                #add to list
            lastpage_href = apks[-1].get('href')
            reg = re.compile(r"=\d+")
            Maxpage = int(reg.search(lastpage_href)[0][1:])
            # print(Maxpage)
            
            for i in range(2,Maxpage+1):
                payload={'p':i}
                res = requests.post(self.url,params=payload,headers=headers)
                markup = res.text
                # print(markup)
                soup = BeautifulSoup(markup,"lxml")
                # print(soup)
                soup = soup.find('div','app_left_list')
                # print(soup)
                apks = soup.find_all('a')
                print('solving the %s:page:%s'%(self.store,i))
                for apk in apks[:10]:
                    href = apk.get('href')
                    if href.startswith(r'/apk?p='):
                        break
                    file.write('https://www.coolapk.com'+href+'\n')                    
                    #add to list
            file.close()
        
        elif self.store == 'anzhi':
            

        else:
            print('Cannot found target appstore:%s'%store)
            exit(1)
    
# def main():
#     craw = crawler('kuan')
#     craw.get_links()

# if __name__ == '__main__':
#     main()