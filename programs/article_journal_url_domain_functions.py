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

#func to process urls for url domain sorting function
#line is PubMed id
def _sort_url_process(line):
    try:
        #build request
        headers = {}
        #internet-explorer user-agent
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        #use nih eutil to get link that redirects to the doi url for each article
        url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id="+line.strip()+"&retmode=ref&cmd=prlinks"
        print(line.strip())
        req = urllib.request.Request(url, headers = headers)
        #use cookie jar to bypass robot blockers
        cj = CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        resp = opener.open(req)
        # url regex: http(s?):\/\/(www\.)?(.*?)\.(com|org|net|gov)
        #use urllib urlparse to extract domain name from url that the doi link redirected to
        found = urllib.parse.urlparse(resp.geturl()).netloc
        #return the the domain name of the doi link of the article and the PubMed id of that article delimeted by ||
        return (found+"||"+line.strip())
    except Exception as e:
        print(str(e))
        #if an error occurs return the domain name as "error:*the error mesage*"
        return ("error:"+str(e)+"||"+line.strip())


def sort_url(id_txt,out_csv,num_threads=10):
    pool = Pool(num_threads)

    #use Pool.map to have the worker pool take ids in chunks from txt
    #and run them though ruby script using the process_line function
    #results will be failed with the ids that failed to dl
    with open(id_txt) as source_file:
        results = pool.map(_sort_url_process, source_file)

    #write the list of failed ids to file
    f = csv.writer(open(out_csv,'w'),lineterminator="\n")
    for i in results:
        f.writerow(i.split("||"))
        
#multiprocessing version of "sort_url"
#faster than the threaded version and opens several different windows
def sort_url_mp(id_txt,out_csv,num_threads=10):
    pool = PoolMP(num_threads)

    #use Pool.map to have the worker pool take ids in chunks from txt
    #and run them though ruby script using the process_line function
    #results will be failed with the ids that failed to dl
    with open(id_txt) as source_file:
        results = pool.map(_sort_url_process, source_file)
    pool.close()
    #write the list of failed ids to file
    f = csv.writer(open(out_csv,'w'),lineterminator="\n")
    for i in results:
        f.writerow(i.split("||"))

def count_domain(in_csv,out_csv):
    domains = {}
    for row in csv.reader(open(in_csv,'r')):
        if row[0] in domains:
            domains[row[0]] = domains[row[0]]+1
        else:
            domains[row[0]] = 1
    w = csv.writer(open(out_csv,'w'),lineterminator="\n")
    for k in domains.keys():
        w.writerow([k,domains[k]])
