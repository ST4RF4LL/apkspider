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
import threading

stores_list = ['kuan','anzhi','wandoujia']

user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0"
headers={"User-Agent":user_agent}
headers2={"User-Agent":user_agent,
'Accept':'text/html,application/xhtm +xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch, br',
'Accept-Language':'zh-CN,zh;q=0.8',
'Connection':'keep-alive'}

def md5(arg):
    md5_hash = hashlib.md5()
    md5_hash.update(arg.encode('utf-8'))
    return md5_hash.hexdigest()

def md5_2(arg):
    md5_hash = hashlib.md5()
    md5_hash.update(arg)
    return md5_hash.hexdigest()

parser = argparse.ArgumentParser(description='A little tool for crawling apks automatically.')
parser.add_argument('-o','--output',help="set the path to the apks have been downloaded.",default=r"/tmp/")
parser.add_argument('-m','--max',help="set the Max amount the apks that will be downloaded",type=int,default=10000)
parser.add_argument('-u','--update',help='check the apk downloaded for the latest version',default=0)
parser.add_argument('-s','--store',help='set the target store to download the apk',default=None)#None means all
args = parser.parse_args()

out_path = args.output
Max_count = args.max
update_flag = args.update
input_store = args.store

download_count = 0

app_stores={'kuan':'https://www.coolapk.com/apk','wandoujia':'https://www.wandoujia.com/category/app'}

class db_opt():
    def db_init(self):
        conn = sqlite3.connect('apkspider.db')
        c= conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS APKINFO(
        apkname text not null,
        platform char(20) not null,
        size int not null,
        md5 char(64) not null
        );
        ''')
        print("database init successfully")

        c.execute('''
        CREATE TABLE IF NOT EXISTS APKLIST(
        id integer primary key autoincrement,
        url text not null,
        platform char(20) not null,
        status int not null DEFAULT 0
        );
        ''')
        # 0 means not downloaded
        # 1 means downloading
        # 2 means done
        print("list database init successfully")
        conn.commit()
        conn.close()


    def db_insert(self,apkname,platform,size,hash_val):
        conn = sqlite3.connect('apkspider.db')
        c= conn.cursor()
        comma = 'INSERT INTO APKINFO(apkname,platform,size,md5)VALUES(\'%s\',\'%s\',%d,\'%s\');'%(apkname,platform,size,hash_val)
        # print(comma)
        c.execute(comma)
        print("insert info into database successfully!")
        conn.commit()
        conn.close()
    
    def db_update(self,apkname,platform,size,hash_val):#My opinion, size and md5 may change together
        conn = sqlite3.connect('apkspider.db')
        c= conn.cursor()
        comma = 'UPDATE APKINFO SET size = %d , md5 = \'%s\' where apkname = \'%s\' and platform = \'%s\';'%(size,hash_val,apkname,platform)
        # print(comma)
        c.execute(comma)
        print("update info into database successfully!")
        conn.commit()
        conn.close()

    def db_delete(self,apkname,platform):
        conn = sqlite3.connect('apkspider.db')
        c= conn.cursor()
        comma = 'delete from APKINFO where apkname = \'%s\' and platform = \'%s\';'%(apkname,platform)
        # print(comma)
        try:
            c.execute(comma)
            print("delete info into database successfully!")
            conn.commit()
            conn.close()    
        except:
            pass
    

    def db_gethash(self,apkname,platform):#select * from APKINFO where apkname = 'XXX' and platform = 'XXX'
        conn = sqlite3.connect('apkspider.db')
        c= conn.cursor()
        comma = 'select md5 from APKINFO where apkname = \'%s\' and platform = \'%s\';'%(apkname,platform)
        # print(comma)
        try:
            cursor = c.execute(comma)
            hash_val = list(cursor)[0][0]
            conn.close()
            return hash_val    
        except:
            return ''

    # this insert maybe not so good as write so frequently
    def list_db_insert(self,url,platform):
        conn = sqlite3.connect('apkspider.db')
        c= conn.cursor()
        comma = 'INSERT INTO APKLIST(url,platform)VALUES(\'%s\',\'%s\');'%(url,platform)
        # print(comma)
        c.execute(comma)
        # print("insert info into database successfully!")
        conn.commit()
        conn.close()

    def list_db_geturl(self,platform):
        with sqlite3.connect('apkspider.db') as conn:
            # TODO to continue last downloading task we can get the url that status = 1
            # but anyway use status !=2 sometimes to dangerous
            comma = r"select id,url from APKLIST where platform = 'wandoujia' and status = 0 order by id limit 1;"
            # print(comma)
            try:
                li = list(conn.execute(comma))
                id = li[0][0]
                url = li[0][1]
                return id,url
            except:
                return -1,''
    
    def list_db_update_status(self,id,status):
        with sqlite3.connect('apkspider.db') as conn:
            comma = r"update APKLIST set status = %d where id = %d;"%(status,id)
            conn.execute(comma)
class downloader():
    def __init__(self):
        self.db = db_opt()
        self.savepath = out_path

    def download(self,filepath,url):
        
        file = requests.get(url,headers=headers,stream=True)
        with open(filepath,'wb') as apk:
            for chunk in file.iter_content(chunk_size=1024):
                if chunk:
                    apk.write(chunk)
        #     apk.write(file.content)
            # hash_val = md5(name)

            # print('filname=%s\nsize=%d\nmd5=%s'%(name,filesize,hash_val))

    def wandoujia(self):
        global download_count
        # with open('downlist.wandoujia','r+') as listfile:
        
        id,link = self.db.list_db_geturl('wandoujia')
        print('link:'+link)
        while link != '' and download_count<Max_count:
            self.db.list_db_update_status(id,1)
            resp = requests.get(link,headers=headers)
            markup = BeautifulSoup(resp.text,'lxml')
            url = markup.find('a','normal-dl-btn').get('href')
            # print(url)
            reg = re.compile(r"/apps/[a-zA-Z.]+")
            name = reg.search(link)[0][6:]

            filepath = self.savepath+name

            old_hash = self.db.db_gethash(name,'wandoujia')
            # print(old_hash)
            if old_hash != '':#means not new file but I have no idea how to get the hash before I download it
                filepath = self.savepath+'temp_'+md5(name)#so I save it as 'temp_md5',then I will check this new file's md5
            res = requests.head(url,allow_redirects=True)
            # true_url = res.headers['Location']
            # res = requests.head(true_url)
            filesize = int(res.headers['Content-Length'])
            # self.download(name,url)
            print('start downloading %s'%name)
            t1 = threading.Thread(target=self.download,args=(filepath,url))
            t1.start()
            self.download_progress(filepath,filesize)
            # calculating hash and add to sqlite3
            with open(filepath,'rb') as file_done:
                hash_val = md5_2(file_done.read())

            print("old_hash:%s\nnew_hash:%s"%(old_hash,hash_val))

            if hash_val == old_hash:# means the same file,delete this file
                #delete
                os.remove(filepath)
                print('same apk,deleted!')
            elif old_hash=='':#means this is a new file
                print('a new apk!')
                self.db.db_insert(name,'wandoujia',int(filesize/1024),hash_val)
                os.rename(filepath,self.savepath+name+'_'+hash_val)
                download_count += 1

            else:
                print('this apk is updated to latest!')
                self.db.db_update(name,'wandoujia',int(filesize/1024),hash_val)
                os.rename(filepath,self.savepath+name+'_'+hash_val)
                download_count += 1

            #delete the url in the download list
            self.db.list_db_update_status(id,2)            
            id,link = self.db.list_db_geturl('wandoujia')
            # coutinue to next downloading
            # link = listfile.readline().replace('\n','')# Important! readline will give the link a '\n'

            # download_count += 1


    def download_progress(self,filepath,filesize):
        with progressbar.ProgressBar(max_value=int(filesize/1024)) as bar:
            current_size=0
            while(current_size<filesize):
                if(os.path.exists(filepath)):
                    current_size = os.path.getsize(filepath)
                    time.sleep(0.1)
                    bar.update(int(current_size/1024))
        print('download success and saved as:%s'%filepath)
            

class crawler():
    def __init__(self,store):
        self.url = app_stores[store]
        self.store = store
        self.db = db_opt()
     
    
    def get_links(self):
        if self.store=='kuan':
            # payload={'p':1}
            # res = requests.post(self.url,params=payload,headers=headers)
            # markup = res.text
            # # print(markup)
            # soup = BeautifulSoup(markup,"lxml")
            # # print(soup)
            # soup = soup.find('div','app_left_list')
            # # print(soup)
            # apks = soup.find_all('a')
            # print('solving the %s:page:%s'%(self.store,1))
            # file = open('./downlist.'+self.store,'a')
            # for apk in apks[:10]:
            #     # print(apk.get('href'))
            #     href = apk.get('href')
            #     file.write('https://www.coolapk.com'+href+'\n')
            #     #add to list
            # lastpage_href = apks[-1].get('href')
            # reg = re.compile(r"=\d+")
            # Maxpage = int(reg.search(lastpage_href)[0][1:])
            # # print(Maxpage)
            
            # for i in range(2,Maxpage+1):
            #     payload={'p':i}
            #     res = requests.post(self.url,params=payload,headers=headers)
            #     markup = res.text
            #     # print(markup)
            #     soup = BeautifulSoup(markup,"lxml")
            #     # print(soup)
            #     soup = soup.find('div','app_left_list')
            #     # print(soup)
            #     apks = soup.find_all('a')
            #     print('solving the %s:page:%s'%(self.store,i))
            #     for apk in apks[:10]:
            #         href = apk.get('href')
            #         if href.startswith(r'/apk?p='):
            #             break
            #         file.write('https://www.coolapk.com'+href+'\n')                    
            #         #add to list
            # file.close()
            exit(1)

        elif self.store == 'anzhi':
            exit(1)
        
        elif self.store == 'wandoujia':
            res = requests.get(self.url,headers=headers)
            markup = BeautifulSoup(res.text,'lxml')
            cates = markup.find_all('li','parent-cate')
            urls = [cate.find('a','cate-link').get('href') for cate in cates]
            # print(urls)
            # with open('./downlist.'+self.store,'a') as file:
            with sqlite3.connect('apkspider.db') as conn:
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
                            # file.write(link+'\n')
                            comma = 'INSERT INTO APKLIST(url,platform)VALUES(\'%s\',\'%s\');'%(link,'wandoujia')
                            conn.execute(comma)
                            # print(link)
                        conn.commit()
                        i += 1

        else:
            print('Cannot found target appstore:%s'%store)
            exit(1)
    
    

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

def test():
    d = db_opt()
    # try:
    #     d.db_init()    
    # except:
    #     pass
    d.db_init()

    # c = crawler('wandoujia')
    # c.get_links()

    down = downloader()
    down.wandoujia()

    # d.db_insert('taobao','test',45,md5('taobao'))
    # d.db_gethash('taobao','test')
    # d.db_delete('taobao','test')
    # d.db_update('taobao','test',50,md5('taobao'))
    

if __name__ == '__main__':
    # main()
    test()