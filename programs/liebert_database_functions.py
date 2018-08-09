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


#func to process ids from inacessable db liebert
def _process_liebert(line):
    try:
        #build request
        headers = {}
        #internet-explorer user-agent string
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        #use nih eutil to get link that redirects to the doi url for each article
        url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id="+line.strip()+"&retmode=ref&cmd=prlinks"
        print(url)
        req = urllib.request.Request(url, headers = headers)
        #site was refusing robot connection so cookie jar is used to bypass
        cj = CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        resp = opener.open(req)

        #check to see if the doi url redirected to liebert db site
        if "liebertpub" in resp.geturl():
            return line
        else:
            return ""
    except Exception as e:
        print(str(e))

    #this return is called if an error occurs while attempting to get the doi url
    #assume its not liebert so it can be checked again
    return ""

#takes input list of PubMed ids and splits based on which ids' doi link redirects to the journal site "liebertpub"
#articles on the site are paywalled and therefore ingnored during pdf collection
#id_txt path to txt with list of ids to b split
#out_txt output path of article ids that are located on liebert site
#not_out_txt output path of article ids that are not located on liebert site
def _get_liebert(id_txt,out_txt, not_out_txt,num_threads=10):
    pool = Pool(num_threads)

    #same Pool.map to map liebert process function to an input list of PubMed ids
    results = []
    with open(id_txt) as source_file:
        results = pool.map(_process_liebert, source_file)
    #write the list of failed ids to file
    with open(out_txt,'w') as f:
        for i in results:
            f.write(i)
    _txt_diff(id_txt,out_txt,not_out_txt)
