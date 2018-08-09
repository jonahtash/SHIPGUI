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
import csv

        
#sorts out the paywalled articles that are inaccesible on the Oxford Journal Website
def _get_ox_paywall(id_txt,out_txt,num_threads=10):
    pool = Pool(num_threads)

    #use Pool.map to have the worker pool take ids in chunks from txt
    #and run them though ruby script using the process_line function
    #results will be failed with the ids that failed to dl
    with open(id_txt) as source_file:
        results = pool.map(_get_ox_paywall_process, source_file)

    #write the list of failed ids to file
    f =open(out_txt,'w')
    for i in results:
        f.write(i)

    
#writes list of failed (paywalled) IDs from Oxford Journal Website
def _get_ox_txt(in_csv,out_txt):
    out = open(out_txt,'a')
    for row in csv.reader(open(in_csv,'r')):
        if row[0]=="academic.oup.com":
            out.write(row[1]+"\n")
    out.close()
    
#Attempts to download the articles from the Oxford Journal Website 
def _get_ox_paywall_process(line):
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
    #Uses the tool 'Beautiful Soup' to parse the HTML of the website
    soup = BeautifulSoup(resp.read(), 'html.parser')
    #checks to see if the document is inaccesible
    if soup.find(id="PermissionsLink"):
        return line
    return ""
