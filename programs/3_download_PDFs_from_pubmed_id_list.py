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

#func to process id in ruby script
def _process_line(line):
    #output PubMed id of document being run through ruby script
    print(line.strip())
    #pass id to ruby script and save output in buffer
    p = subprocess.Popen("ruby pubmedid2pdf.rb "+line,shell = False,
                         stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.wait()
    #the ruby script uses alot of console warnings that mainly come to stderr
    #if the dl failed return the id to be added to list of failed ids
    if "failed" in str(p.stderr.read()):
        return line
    #if the dl is successful return no id (empty string)
    return ""

#run ruby script on list of ids at file_path and output failed ids
#to kickback_loc. Optional num_threads number of threads to run- default 10
#recommended to run this function over multiprocessing
def run_id_ruby(file_path,kickback_path,num_threads=10):
    #record start time to calculate total runtime later
    start = datetime.now()

    #init pool of workers from specified number
    #this is how many downloads will run in parallel
    pool = Pool(num_threads)

    #use Pool.map to have the worker pool take ids in chunks from txt
    #and run them though ruby script using the _process_line function
    #results will be failed with the ids that failed to dl
    with open(file_path) as source_file:
        results = pool.map(_process_line, source_file)

    #write the list of failed ids to file
    with open(kickback_path,'w') as f:
        for i in results:
            f.write(i)
    return datetime.now()-start

#run ruby script on list of ids at file_path and output failed ids
#to kickback_loc. Optional num_threads number of threads to run- default 10
#multiprocessing version uses processes which opens multiple windows, not neccesary for ruby function
def run_id_ruby_mp(file_path,kickback_path,num_threads=10):
    #record start time to calculate total runtime later
    start = datetime.now()

    #init pool of workers from specified number
    #this is how many downloads will run in parallel
    pool = PoolMP(num_threads)

    #use Pool.map to have the worker pool take ids in chunks from txt
    #and run them though ruby script using the _process_line function
    #results will be failed with the ids that failed to download
    with open(file_path) as source_file:
        results = pool.map(_process_line, source_file)

    #write the list of failed ids to file
    with open(kickback_path,'w') as f:
        for i in results:
            f.write(i)
    return datetime.now()-start

