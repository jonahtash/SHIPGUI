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


# trys to download from URLs that have previously failed
def _download_pdf_errors(download_url,pmed_id,pdf_output_dir,kickback_dir):
    e404 = open(kickback_dir+"error_404.txt",'a')
    e403_ban = open(kickback_dir+"error_403_ipBan.txt",'a')
    e403_rem = open(kickback_dir+"error_403_rem.txt",'a')
    try:
        #assemble http request. PMC is sus if you don't have User-Agent header
        headers = {}
        #set agent to Internet-Explorer
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        req = urllib.request.Request(download_url, headers = headers)
        resp = urllib.request.urlopen(req)
        with open("./"+pdf_output_dir+pmed_id+".pdf",'wb') as f:
            f.write(resp.read())
            f.close()
    #If there is an error 404 or error 403, then those IDs are written to a txt
    except Exception as e:
        print(str(e))
        if e.code == 404:
            e404.write(download_url[download_url.index("PMC"):download_url.index("/pdf/")]+"+"+pmed_id+"\n")
        #PubMed Central Website bans batch downloading after a period of time
        #If the computer's IP gets banned by PMC, all left over ID's are written to a txt
        if e.code == 403:
            if "Internet connection (IP address) was used to download content in bulk" in str(e.read()):
                e403_ban.write(download_url[download_url.index("PMC"):download_url.index("/pdf/")]+"+"+pmed_id+"\n")
            else:
                e403_rem.write(download_url[download_url.index("PMC"):download_url.index("/pdf/")]+"+"+pmed_id+"\n")
    e404.close()
    e403_ban.close()
    e403_rem.close()


def _unpack_error(s):
    a = s.split("+")
    print(a[0]+" "+a[1].strip())
    _download_pdf_errors("https://www.ncbi.nlm.nih.gov/pmc/articles/"+a[0]+"/pdf/",
                        a[1].strip(),a[2],a[3])
#regular threaded function
#deafult num threads is 2
#function to name PDFs
def get_error(id_file_path,pdf_output_dir,kickback_dir,num_thread=2):
    pdf_output_dir = _clean_path(pdf_output_dir)
    pool = Pool(num_thread)
    pack = []
    for line in open(id_file_path,'r'):
        pack.append(line+"+"+pdf_output_dir+"+"+kickback_dir)
    results = pool.map(_unpack_error,pack)

#multiprocessing version of get_error
#default number of threads is 2
def get_error_mp(id_file_path,pdf_output_dir,kickback_dir,num_thread=2):
    pdf_output_dir = _clean_path(pdf_output_dir)
    kickback_dir = _clean_path(kickback_dir)
    pool = PoolMP(num_thread)
    pack = []
    for line in open(id_file_path,'r'):
        pack.append(line+"+"+pdf_output_dir+"+"+kickback_dir)
    results = pool.map(_unpack_error,pack)
    pool.close()
    