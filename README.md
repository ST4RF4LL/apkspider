# apkspider
# Apk爬虫开发文档
## 给创新实践的作业一个帝王级的待遇
## 功能
    1.  编写针对专门市场的APK下载工具，下载内容包括：应用名称、所在网址、所处的类别、说明文字、下载次数、评分、APK文件等可从市场获取的信息；
    2.  提供实时的下载进度和过程；
    3.  提供实时的统计信息，如已下载APK的数量、总大小、成功数量、失败数量等；
    4.  支持中断后下载：如果某次下载被中断，下次启动时可选择继续下载；
    5.  提供应用市场的信息，如包含的应用数量、已下载数量等。
## 要求
    1. 支持专门的安卓应用市场下载，如豌豆荚、百度、华为、安智等，在项目报告中提供这些应用市场如何组织APK，以及提供Web下载服务的过程；
    2. APK文件存储在同一个文件夹中，APK名称可用该文件的MD5值，其他信息存储到SQLite3数据库中；
    3. 提供一种方法，判断某个应用是否已经被下载到本地，避免重复下载(Bloom Filter 与 KV存储)；
    4. 提供一种方法，判断市场中是否出现了新的应用，实现本地与市场的同步更新；
    5. 程序设计语言不限，可为命令行或者为GUI形式；
    6. 每个功能输出的结果都能输出到屏幕或者输出到文件；
    7. 请勿直接复制粘贴他人代码。
## 需求分析综述
1. 下载进度条
    - 使用python-progressbar2库
2. 支持断点续传以及重启继续任务
    - 考虑用文件保存未完成的任务list
3. 运行参数
    - 用argparse管理
4. 下载前预估空闲空间
## argparse
- `-o`:`--output`
- `-c`:`--continue`
- `-u`:`--update`
- `-s`:``--store`
- `-r`:`refresh`
- 
<!-- - `-c`:--continue -->
- 如果不给参数 什么都不做

## sqlite3
Apkname platform md5 update_time size download_status(0:no,1:downloading,2:done)  (optional:version)

实际:  apkname platform size md5
## file download
- 我个人想要保留某一apk的没一个版本，我决定命名法为: ApkName_md5
- get:filesize:这里`普通下载`给的链接有一个重定向，即原链接的content_length=0，需要重定向链接才能获取filesize

## download list
用来临时存储下载任务的文件，暂时仅使用同一个list文件，日后根据实际情况决定是否拆分
可能需要根据不同的商城来区分，因为这是app的链接，下载链接还需要从该网页中获取，已经app信息从中提取放入sqlite3
逻辑:websolver爬取网页获取各app页面->spider获取app信息存入sqlite3->下载

## progressbar
需要进度条，就需要给下载一个独立的线程  
接着将progressbar的maxvalue设定为apk的size，进度设定为当前的下载量

## TODO
1. 还没实现断点续传以及重启脚本继续下载任务
2. 还没做下载列表逐行删除


## 改方案
发现一个挺致命的问题，针对TODO里的第二条'下载列表逐行删除'，python貌似没这个功能  
那我现在的想法就是弃用弱智的文件读写，改为数据库读写

## 大改方案
豌豆荚太酷炫了，竟然把翻页式的改成动态加载的了


# v0.9
1. 把豌豆荚的爬虫修好了
2. 考虑写一些断点续传
3. 命令行参数的问题等找大师傅问问再改

# v0.95
1. argparse中包含了action="store_ture"的用法，命令行参数基本搞定了
2. 继续上次下载的功能依旧这么蛇皮