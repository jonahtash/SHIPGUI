from multiprocessing import Pool as PoolMP
from multiprocessing.dummy import Pool
from multiprocessing import freeze_support
import csv
import subprocess
import xml.etree.ElementTree as ET
        

# Removes html content from csv file 
def rem_html_csv(csv_in,csv_out):
    csvf = csv.reader(open(csv_in,'r',encoding='utf-8'))
    csvw = csv.writer(open(csv_out,'w',encoding='utf-8-sig'),lineterminator='\n')
    for row in csvf:
        br = []
        diff = 0
        for i in range(len(row)):
            orig=row[i]
            bs = re.sub(r'<\/?(.*?)>'," ",row[i],flags=re.DOTALL)
            bs = re.sub(r'\[\[{(.*?)}\]\]'," ",bs)
            bs += " "
            regs = [[r'http(.*?)(\s)', ' '],[r'&(.*?)(\s|;)', ' '],[r'\t* *\n','\n'],[r'(\n{2,})','\n'],[r'(\r{2,})','\r'],[r'( {2,})',' ']]
            for reg in regs:
                bs = re.sub(reg[0],reg[1],bs)
            br.append(bs.strip())
            if(i==1):
                diff = (len(orig)-len(bs))
        br.append(diff)
        csvw.writerow(br)

        
# Removes html content from xlsx file
def rem_html_xls(xls_in,csv_out):
    xlsf = pd.read_excel(xls_in,encoding='utf-8',header=None)
    xlsf = xlsf.astype(str)
    csvw = csv.writer(open(csv_out,'w',encoding='utf-8-sig'),lineterminator='\n')
    for row in xlsf.itertuples():
        br = []
        diff = 0
        for i in range(1,len(row),1):
            orig=str(row[i])
            bs = re.sub(r'<\/?(.*?)>'," ",str(row[i]),flags=re.DOTALL)
            bs = re.sub(r'\[\[{(.*?)}\]\]'," ",bs)
            bs += " "
            regs = [[r'http(.*?)(\s)', ' '],[r'&(.*?)(\s|;)', ' '],[r'\t* *\n','\n'],[r'(\n{2,})','\n'],[r'(\r{2,})','\r'],[r'( {2,})',' ']]
            for reg in regs:
                bs = re.sub(reg[0],reg[1],bs)
            br.append(bs.strip())
            if(i==1):
                diff = (len(orig)-len(bs))
        br.append(diff)
        csvw.writerow(br)
