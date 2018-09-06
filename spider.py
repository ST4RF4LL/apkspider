#! /usr/bin/env python3
# coding: utf-8

import argparse


app_stores=['https://www.coolapk.com/apk?p=1']

parser = argparse.ArgumentParser(description='A little tool for crawling apks automatically.')
parser.add_argument('-o','--output',help="set the path to the apks have been downloaded.",default=r"/tmp/")
parser.add_argument('-M',help="set the Max amount the apks that will be downloaded",type=int)
args = parser.parse_args()


def main():
    pass

if __name__ == '__main__':
    main()