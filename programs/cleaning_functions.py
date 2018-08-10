import os
from multiprocessing import Pool as PoolMP
from multiprocessing.dummy import Pool
from multiprocessing import freeze_support
from datetime import datetime
import subprocess
import csv
import urllib.request
from io import StringIO
import unicodedata
import ctypes
import requests
import sqlite3
import json
import re
from http.cookiejar import CookieJar
from bs4 import BeautifulSoup
import pandas as pd
import shutil
import xml.etree.ElementTree as ET

#Removes duplicate lines in txt file located at in_path
#Outputs to out_path
def _remove_dupes_txt(in_path, out_path):
    lines_seen = set()
    outfile = open(out_path, "w")
    for line in open(in_path, "r"):
        if line not in lines_seen:
            outfile.write(line)
            lines_seen

def _txt_diff(txt1,txt2,out_txt):
    t1 = open(txt1,'r').readlines()
    t2 = open(txt2,'r').readlines()
    open(out_txt,'w').writelines(list(set(t1)-set(t2)))


def rem_pmcid(in_path,out_path):
    with open(in_path,'r') as inF:
        with open(out_path,'w') as outF:
            for line in inF:
                outF.write(line.split('+')[1])

def _split_every(n, s):
    return [ s[i:i+n] for i in range(0, len(s), n) ]

def _clean_path(path):
    if path[-1]!="/":
        return path+"/"
    else:
        return path

def _clean_sql(s):
    return ''.join([i if ord(i) < 128 else '' for i in s]).replace("\t",' ').replace("\n",' ').replace("\r"," ")

