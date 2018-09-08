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
- 如果不给参数 则check是否有未完成任务以及check

## APK stores
1. 酷安：下载链接通过js脚本onDownloadApk动态获取，就在页面源码里
2. 豌豆荚：应用主页上的下载链接应该是用来下载豌豆荚的，需要点击进去，使用普通下载获取链接;主页面上市惰性加载
```javascript
<script type="text/javascript">
    function onDownloadApk($downloadId) {
        if ($downloadId) {
            window.location.href = "https://dl.coolapk.com/down?pn=me.ele&id=MTMwMDA&h=38f02906pepw2b&from=click";
        } else {
            window.location.href = 'https://dl.coolapk.com/down?pn=com.coolapk.market&id=NDU5OQ&h=38f02906pepw2b&from=click';
        }
    }
</script>
```

## sqlite3
Apkname platform md5 update_time size download_done  (optional:version)