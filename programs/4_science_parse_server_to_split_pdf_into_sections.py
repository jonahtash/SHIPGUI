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

#connects to the science-parse server
#server is hosted locally on the machine
#science-parse creates JSON files which contain the PDF contents seperated by section
def _post_science_parse(s):
    a=s.split("+")
    print(a[0])
    try:
        with open(a[0], 'rb') as f:
            r = requests.post('http://localhost:8080/v1', files={a[0]: f})
            open(a[1]+a[0].split('/')[-1][0:-4]+'.json','w',encoding='utf-8').write(r.text)
    #prints an error if the PDF cannot be parsed
    except Exception as e:
        print("ERROR "+str(e))
#gets JSON file from science parse server and saves it to directory
def get_pdf_json(pdf_dir,out_dir,num_thread=2):
    pdf_dir = _clean_path(pdf_dir)
    out_dir = _clean_path(out_dir)
    pool = Pool(num_thread)
    pack = []
    for line in os.listdir(pdf_dir):
        pack.append(pdf_dir+line+"+"+out_dir)
    results = pool.map(_post_science_parse,pack)
    
#multiprocessing version of "get_pdf_json"
#default number of threads = 2
def get_pdf_json_mp(pdf_dir,out_dir,num_thread=2):
    pdf_dir = _clean_path(pdf_dir)
    out_dir = _clean_path(out_dir)
    pool = PoolMP(num_thread)
    pack = []
    try:
        for line in os.listdir(pdf_dir):
            pack.append(pdf_dir+line+"+"+out_dir)
    except Exception as e:
        print(str(e))
    results = pool.map(_post_science_parse,pack)
    pool.close()
