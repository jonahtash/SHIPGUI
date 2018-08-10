#make list of PubMed ids from PubMed csv
import os
from multiprocessing import Pool as PoolMP
from multiprocessing.dummy import Pool
from multiprocessing import freeze_support
import subprocess
import csv


def count_heads(csv_file_path):
    seen = []
    for row in csv.reader(open(csv_file_path,'r')):
        if row[0] not in seen:
            seen.append(row[0])
    return len(seen)

def sort_inacessable_csv(csv_file_path, good_out_path, bad_out_path):
    good_pdf= csv.writer(open(good_out_path, 'w'),lineterminator="\n")
    bad_pdf = csv.writer(open(bad_out_path, 'w'),lineterminator="\n")
    with open(csv_file_path, encoding='utf-8') as csvf:
        readCSV = csv.reader(csvf, delimiter=',')
        for row in readCSV:
            if "doi:" not in row[3] and "PMCID" not in row[7]:
                bad_pdf.writerow(row)
            else:
                good_pdf.writerow(row)


def get_pmedid_csv(csv_file_path,output_path):
    out = open(output_path,'w')
    with open(csv_file_path, encoding='utf-8') as csvf:
        re = csv.reader(csvf, delimiter=',')
        for row in re:
            out.write(row[9]+"\n")
    out.close()



#Removes duplicate lines in txt file located at in_path
#Outputs to out_path
def _remove_dupes_txt(in_path, out_path):
    lines_seen = set()
    outfile = open(out_path, "w")
    for line in open(in_path, "r"):
        if line not in lines_seen:
            outfile.write(line)
            lines_seen.append(line)

def _txt_diff(txt1,txt2,out_txt):
    t1 = open(txt1,'r').readlines()
    t2 = open(txt2,'r').readlines()
    open(out_txt,'w').writelines(list(set(t1)-set(t2)))


#Take PubMed csv at csv_file_path.
#Make list of entries with PMCID format "PMCID+PUBMEDID" at pmc_path.
#Make list of entries with no PMCID at nopmc_path.
def get_pmcid_csv(csv_file_path,pmc_path,nopmc_path):
    pmc = open(pmc_path,'w')
    nopmc = open(nopmc_path,'w')
    with open(csv_file_path, encoding='utf-8') as csvf:
        re = csv.reader(csvf, delimiter=',')
        for row in re:
            if "PMCID:" in row[7]:
                pmc.write(row[7].split("PMCID:")[1]+"+"+row[9]+"\n")
            else:
                nopmc.write(row[9]+"\n")
    pmc.close()
    nopmc.close()

#Add PMCID to PUBMEDIDs in pmed_id_path txt.
#Output results in format "PMCID+PUBMEDID" to output_path.
def csv_add_pcmid(csv_file_path,pmed_id_path,output_path):
    out = open(output_path,'w')
    for i in open(pmed_id_path,'r'):
        print(i.strip())
        with open(csv_file_path, encoding='utf-8') as csvf:
               re = csv.reader(csvf, delimiter=',')
               for row in re:
                   if(row[9] in i):
                       out.write(row[7].split("PMCID:")[1]+"+"+row[9]+"\n")
                       break
    out.close()
