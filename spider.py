#! /usr/bin/env python3
# coding: utf-8

import argparse
import progressbar
import os
import sys
import time
import requests
import hashlib


def md5(arg):
    md5_hash = hashlib.md5()
    md5_hash.update(arg)
    return md5_hash.hexdigest()

parser = argparse.ArgumentParser(description='A little tool for crawling apks automatically.')
parser.add_argument('-o','--output',help="set the path to the apks have been downloaded.",default=r"/tmp/")
parser.add_argument('-M',help="set the Max amount the apks that will be downloaded",type=int)
parser.add_argument('-u','--update',help='check the apk downloaded for the latest version',default=0)
parser.add_argument('-s','--store',help='set the target store to download the apk',default=None)#None means all
args = parser.parse_args()

out_path = args.output
Max_count = args.m
update_flag = args.update
store = args.store

def main():
    pass
if __name__ == '__main__':
    main()