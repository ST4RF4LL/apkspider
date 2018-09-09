#! /usr/bin/env python3
# coding: utf-8

import argparse
import progressbar
import os
import sys
import time
import requests
import hashlib
import sqlite3
import re
import lxml
from bs4 import BeautifulSoup

stores_list = ['kuan','anzhi','wandoujia']

user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
headers={"User-Agent":user_agent}
headers2={"User-Agent":user_agent,'Connection': 'keep-alive'}

def md5(arg):
    md5_hash = hashlib.md5()
    md5_hash.update(arg)
    return md5_hash.hexdigest()

parser = argparse.ArgumentParser(description='A little tool for crawling apks automatically.')
parser.add_argument('-o','--output',help="set the path to the apks have been downloaded.",default=r"/tmp/")
parser.add_argument('-m','--max',help="set the Max amount the apks that will be downloaded",type=int)
parser.add_argument('-u','--update',help='check the apk downloaded for the latest version',default=0)
parser.add_argument('-s','--store',help='set the target store to download the apk',default=None)#None means all
args = parser.parse_args()

out_path = args.output
Max_count = args.max
update_flag = args.update
input_store = args.store

app_stores={'kuan':'https://www.coolapk.com/apk','wandoujia':'https://www.wandoujia.com/category/app'}


class crawler():
    def __init__(self,store):
        self.url = app_stores[store]
        self.store = store
    def get_links(self):
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
            exit(1)
        
        elif self.store == 'wandoujia':
            res = requests.get(self.url,headers=headers)
            markup = BeautifulSoup(res.text,'lxml')
            cates = markup.find_all('li','parent-cate')
            urls = [cate.find('a','cate-link').get('href') for cate in cates]
            # print(urls)
            file = open('./downlist.'+self.store,'a')
            for child_page in urls:
                i=1
                while i :
                    print('get page:%d\n'%i)
                    url = child_page + r'/%d'%i
                    res = requests.get(url,headers=headers)
                    markup = BeautifulSoup(res.text,'lxml')
                    cates = markup.find_all('li','card')
                    if len(cates)==0:
                        break;
                    links = [cate.find('a','name').get('href') for cate in cates]
                    for link in links:
                        file.write(link+'\n')
                        print(link)
                    i += 1
            file.close()


        else:
            print('Cannot found target appstore:%s'%store)
            exit(1)
    
    def download(filename,url):
        filename = md5(filename.encode('utf-8'))
        res = requests.head(url)
        filesize = round(float(res.headers['Content-Length']) / 1048576, 2)
        file = requests.get(url,headers=headers,timeout=2)
        with open(filename,'wb') as apk:
            apk.write(file.content)
            print('download success\n')

def main():
    # print(input_store)
    if input_store in stores_list:
        cr = crawler(input_store)
        cr.get_links()
        # download(input_store)
    elif input_store == None:
        for i in stores_list:
            cr = crawler(i)
            # download(i)
    else:
        exit(1)
    # crawler.download('taobao','https://android-apps.pp.cn/fs08/2018/08/16/5/110_b2a11955d308c069f07033959edc1226.apk?yingid=pp_client&packageid=400685613&md5=03661e11fb66e5dd97c225f3ae478f45&minSDK=14&size=91718666&shortMd5=8c65554e572b38a1f82b92d496b23b3e&crc32=3329255329')


if __name__ == '__main__':
    main()