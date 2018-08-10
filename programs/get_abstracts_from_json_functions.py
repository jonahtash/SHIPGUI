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


def _process_get_abstracts(line):
    line=line.strip()
    headers = {}
    #internet-explorer user-agent
    headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
    #use nih eutil to get link that redirects to the doi url for each article
    url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="+line+"&rettype=Abstract"
    print(line)
    req = urllib.request.Request(url, headers = headers)
    #use cookie jar to bypass robot blockers
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    resp = opener.open(req)
    root = ET.fromstring(resp.read())
    abst = root.find('PubmedArticle').find('MedlineCitation').find('Article').find('Abstract').find('AbstractText').text if root.find('PubmedArticle').find('MedlineCitation').find('Article').find('Abstract') else ""
    title = root.find('PubmedArticle').find('MedlineCitation').find('Article').find('ArticleTitle').text.strip()
    journal_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id="+line+"&retmode=ref&cmd=prlinks"
    if not abst:
        abst = ""
    return line+"**"+title+"^&^&"+journal_url+"$%$%"+abst
          
def get_abstracts_mp(txt_ids_in,csv_abstracts_out,num_threads=10):
    pool = PoolMP(num_threads)

    #use Pool.map to have the worker pool take ids in chunks from txt
    #and run them though ruby script using the process_line function
    #results will be failed with the ids that failed to dl
    with open(txt_ids_in) as source_file:
        results = pool.map(_process_get_abstracts, source_file)

    #write the list of failed ids to file
    csvf =csv.writer(open(csv_abstracts_out,'w',encoding='utf-8-sig'),lineterminator="\n")
    csvf.writerow(["PubMed Id","Title","Journal URL","Abstract"])
    for i in results:
        id_index = i.index("**")
        title_index = i.index("^&^&")
        abst_index = i.index("$%$%")
        csvf.writerow([i[:id_index],i[id_index+2:title_index],i[title_index+4:abst_index],i[abst_index+4:]])

def get_abstracts(txt_ids_in,csv_abstracts_out,num_threads=10):
    pool = Pool(num_threads)

    #use Pool.map to have the worker pool take ids in chunks from txt
    #and run them though ruby script using the process_line function
    #results will be failed with the ids that failed to dl
    with open(txt_ids_in) as source_file:
        results = pool.map(_process_get_abstracts, source_file)

    #write the list of failed ids to file
    csvf =csv.writer(open(csv_abstracts_out,'w',encoding='utf-8-sig'),lineterminator="\n")
    csvf.writerow(["PubMed Id","Title","Journal URL","Abstract"])
    for i in results:
        id_index = i.index("**")
        title_index = i.index("^&^&")
        abst_index = i.index("$%$%")
        csvf.writerow([i[:id_index],i[id_index+2:title_index],i[title_index+4:abst_index],i[abst_index+4:]])


def extract_journal_ids(csv_in,txt_ids_out,site_domain):
    in_csv = csv.reader(open(csv_in,'r',encoding='utf-8'))
    out=open(txt_ids_out,'w',encoding='utf-8')
    for row in in_csv:
        if site_domain ==row[0]:
            out.write(row[1]+"\n")
    out.close()
