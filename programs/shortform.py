import csv, string, re, sqlite3, math

elements = ['ac', 'ag', 'al', 'am', 'ar', 'as', 'at', 'au', 'b', 'ba', 'be', 'bh', 'bi', 'bk', 'br', 'c', 'ca', 'cd', 'ce', 'cf', 'cl', 'cm', 'cn', 'co', 'cr', 'cs', 'cu', 'db', 'ds', 'dy', 'er', 'es', 'eu', 'f', 'fe', 'fl', 'fm', 'fr', 'ga', 'gd', 'ge', 'h', 'he', 'hf', 'hg', 'ho', 'hs', 'i', 'in', 'ir', 'k', 'kr', 'la', 'li', 'lr', 'lu', 'lv', 'mc', 'md', 'mg', 'mn', 'mo', 'mt', 'n', 'na', 'nb', 'nd', 'ne', 'nh', 'ni', 'no', 'np', 'o', 'og', 'os', 'p', 'pa', 'pb', 'pd', 'pm', 'po', 'pr', 'pt', 'pu', 'ra', 'rb', 're', 'rf', 'rg', 'rh', 'rn', 'ru', 's', 'sb', 'sc', 'se', 'sg', 'si', 'sm', 'sn', 'sr', 'ta', 'tb', 'tc', 'te', 'th', 'ti', 'tl', 'tm', 'ts', 'u', 'v', 'w', 'xe', 'y', 'yb', 'zn', 'zr']
blacklist = ['with', 'at', 'from', 'in', 'to', 'of', 'for', 'by', 'into', 'upon', 'and']
stoppers = ['as', 'a', 'an', 'the', 'because', 'or', 'the']
doubles = ['Infrared', 'infrared', '-infrared']

class StdevFunc:
    def __init__(self):
        self.M = 0.0
        self.S = 0.0
        self.k = 1

    def step(self, value):
        if value is None:
            return
        tM = self.M
        self.M += (value - tM) / self.k
        self.S += (value - tM) * (value - self.M)
        self.k += 1

    def finalize(self):
        if self.k < 3:
            return 0
        return math.sqrt(self.S / (self.k-2))

def _split_by_abbrevs(toSplit): # splits a string by ")", but only if the term in parentheses matches criteria for abbreviations
    out = []
    split_indices = [0]
    index = 0
    while toSplit.find("(",index) != -1:
        index = toSplit.find("(",index) + 1
        endex = toSplit.find(")",index)
        abbreviation = toSplit[index:endex]
        # Criteria for abbreviations should go below
        if not bool(re.search(r'\d+', abbreviation)) and 1 < len(abbreviation) < 7 and bool(re.search("[A-Z]", abbreviation)) and abbreviation.lower() not in elements and not bool(re.search("^(IX|IV|V?I{0,3})$", abbreviation)) and not bool(re.search("^[A-Z]{1}[a-z]{3,}$", abbreviation)) and abbreviation[0] not in string.punctuation:
            split_indices.append(endex)
    split_indices.append(len(toSplit))
    for qqq in range(len(split_indices)-1):
        out.append(toSplit[split_indices[qqq] : split_indices[qqq+1]])
    return out

def _look_back(put,ID): # Pass in string delimited by ")"
    put = str(put)
    out = []
    split_input=[]
    # split_input should contain in index 0 the abbreviation and in index 1 the string that preceeds it
    split_index = put.rfind('(',0,-2) +1
    split_input.append(put[0:split_index - 2])
    split_input.append(put[split_index: len(put)])
    if len(split_input[0]) == 0:
        return
    back = 0
    # back stores the number of words to look back, based on the abbreviation
    out.append(" (" + split_input[1] + ")")
    for i in split_input[1]:
        if i not in string.punctuation and i not in string.whitespace:
            back += 1
    if bool(re.search(".*[s]$", split_input[1])): # Plurals often have an 's' tacked onto the end of the abbreviation proper - this accounts for that
        back -= 1
    end_index = len(split_input[0])
    if split_input[0][len(split_input[0])-1] in string.whitespace:
        end_index -= 1
    q = 0
    # This loop will look back as many words as there are characters in the abbreviation, except in special cases noted at the end
    while q < back:
        beg_index = end_index - 1
        if beg_index < 0:
            break
        while split_input[0][beg_index] not in string.whitespace and split_input[0][beg_index] != '-':
            beg_index -= 1
            if beg_index <= 0:
                break
        if split_input[0][beg_index] == '-':
            nex = split_input[0][beg_index : end_index]
        else:
            nex = split_input[0][beg_index + 1 : end_index]
        # At this point nex will have the next word stored in it
        # Below are the conditions under which nex will be added to out
        if len(nex) == 0:
            break
        if nex[len(nex) - 1] == ',' or (nex[len(nex) - 1] == '.' and len(nex) > 2) or nex.lower() in stoppers or ">" in nex:
            break
        out.append(nex)
        if len(nex) > 14 and nex[0].lower() == split_input[1][0].lower() and not split_input[1][0] == split_input[1][len(split_input[1])-1]:
            break
        end_index = beg_index
        if nex.lower() not in blacklist: #blacklisted words don't count towards the total
            q += 1
        if nex.lower() in doubles or split_input[0][beg_index + 1 : end_index].lower() in doubles: #doubles will count twice
            q += 1
        if nex.lower() == 'x' and out[len(out)-2].lower() == '-ray':
            q -= 1
        # end while loop
    out.reverse()
    while out[0] in blacklist or out[0] in string.punctuation:
        del out[0]
    if out[0][0] in string.punctuation:
        out[0] = out[0][1:len(out[0])]
    if bool(re.search("^[0-9]{1,2}[\)]{1}", out[0])):
        out[0] = out[0].split(')' ,1)[1]
    real_out = ["",""]
    for index in range(len(out)-1):
        real_out[0] += out[index]
        if out[index + 1][0] != '-':
            real_out[0] += " "
    real_out[1] = out[len(out)-1]
    letters = 0
    for maybe_letter in real_out[0]:
        if maybe_letter in string.ascii_letters:
            letters += 1
    if letters < len(real_out[0])/2:
        return
    real_out.append(ID)
#   real_out.append(put)
    real_out[0] = real_out[0].lstrip()
    if len(real_out[0]) == 0 or not real_out[0][0].lower() == real_out[1][2].lower() or real_out[0].lower() in elements:
        return
    for ab in real_out[1]:
        if ab.lower() not in real_out[0].lower() and ab.lower() in string.ascii_lowercase:
            return
    return real_out


def _process(input, searchIndex, IDIndex, db, tab):
    raw = []
    for readNext in input:
        entry = _split_by_abbrevs(readNext[searchIndex])
        ID = readNext[IDIndex]
        for abrev in entry:
            put = _look_back(abrev,ID)
            if put not in raw and put is not None:
                raw.append(put)
    conn = sqlite3.connect(db)
    conn.create_aggregate("stdev", 1, StdevFunc)
    curse = conn.cursor()
    curse.execute("CREATE TABLE IF NOT EXISTS " + tab + "(longs TEXT, short TEXT, ID TEXT, freq INT, stdv FLOAT, avrge FLOAT, suspect TEXT)")
    # Put raw values in SQL table
    for row in raw:
        to_insert = [row[0].lower().strip(),row[1].strip(),row[2]]

        curse.execute("INSERT INTO "+tab+"(longs, short, ID) VALUES (?,?,?)", to_insert)
    # Mark suspicious entries
    curse.execute("SELECT DISTINCT longs, short FROM " + tab)
    for unique in curse.fetchall():
        curse.execute("SELECT COUNT(longs) FROM " + tab + " WHERE longs = ? AND short = ?", unique)
        freq = int(curse.fetchone()[0])
        curse.execute("UPDATE " + tab + " SET freq = ? WHERE longs = ? AND short = ?",(freq, unique[0], unique[1]))
        check_unique = []
        check_unique.append(unique[0])
        check_unique.append(unique[1])
        to_cut = []
        for ind in range(len(check_unique[1])):
            if check_unique[1][ind] in string.ascii_lowercase or (check_unique[1][ind] in string.punctuation and not (check_unique[1][ind] == "(" or check_unique[1][ind] == ")")):
                to_cut.append(ind)
        if not len(to_cut) == 0:
            replacR = check_unique[1][0:to_cut[0]]
            for bb in range(len(to_cut)-1):
                replacR += check_unique[1][to_cut[bb]+1:to_cut[bb+1]]
            if not to_cut[len(to_cut) - 1] + 1 == len(check_unique[1]):
                replacR += check_unique[1][to_cut[len(to_cut)-1]+1:len(check_unique[1])]
            check_unique[1] = replacR

        check_unique[0] = check_unique[0].replace("x-ray","xray")
        check_unique[0] = check_unique[0].replace("ultraviolet","ultra violet")
        spaceSplits = check_unique[0].split()
        for worb in spaceSplits:
            if worb.lower() in blacklist:
                spaceSplits.remove(worb)
        hyphenSplits = []
        for tip in spaceSplits:
            for crop in tip.split("-"):
                hyphenSplits.append(crop)
        for pos in hyphenSplits:
            if len(pos) == 0:
                hyphenSplits.remove(pos)
        suspicious = "No"
        if not len(check_unique[1])-2 == len(hyphenSplits):
            suspicious = "Yes"
        else:
            try:
                for index in range(1,len(check_unique[1])-1):
                    if not check_unique[1][index].lower() == hyphenSplits[index-1][0].lower():
                        suspicious = "Yes"
            except:
                print(hyphenSplits + " | " + unique[1])

        curse.execute("UPDATE " + tab + " SET suspect = ? WHERE longs = ? AND short = ?", (suspicious, unique[0], unique[1]))
    # Calculate standard deviation and average, write to SQL table
    curse.execute("SELECT DISTINCT short FROM " + tab)
    x=curse.fetchall()
    for unique in x:
        curse.execute("SELECT stdev(freq) FROM " + tab + " WHERE short = ?", (unique[0].strip(),))
        #print(unique[0])
        z=curse.fetchone()[0]
        curse.execute("UPDATE " + tab + " SET stdv = ? WHERE short = ?", (z,unique[0].strip()))
        curse.execute("SELECT AVG(freq) FROM " + tab + " WHERE short = ?", (unique[0].strip(),))
        zz = curse.fetchone()[0]
        curse.execute("UPDATE " + tab + " SET avrge = ?  WHERE short = ?", (zz,unique[0].strip()))
    curse.execute("SELECT DISTINCT short FROM " + tab)
    x=curse.fetchall()
    for unique in x:
        curse.execute("SELECT stdev(freq) FROM " + tab + " WHERE short = ?", (unique[0].strip(),))
        #print(unique[0])
        z=curse.fetchone()[0]
        curse.execute("UPDATE " + tab + " SET stdv = ? WHERE short = ?", (z,unique[0].strip()))
        curse.execute("SELECT AVG(freq) FROM " + tab + " WHERE short = ?", (unique[0].strip(),))
        zz = curse.fetchone()[0]
        curse.execute("UPDATE " + tab + " SET avrge = ?  WHERE short = ?", (zz,unique[0].strip()))
    if db != ":memory:":
        conn.commit()
    curse.execute("SELECT * FROM " + tab)
    return curse.fetchall()

def grab_table_write_table(fileIn, fileOut, abstractName, IDName): # Accepts two filepaths and two strings
    readR = csv.reader(open(fileIn, newline = "")) # readR will be used to read fileIn row by row (make sure it is a csv)
    firstRow = next(readR) # make sure fileIn has headers as well
    searchIndex = firstRow.index(abstractName)
    IDIndex = firstRow.index(IDName) # use searchIndex and IDIndex as indices to search and ID respectively
    processed = _process(readR,searchIndex,IDIndex,":memory:","tab")
    out = open(fileOut, "w", newline = "")
    writeR = csv.writer(out, quoting = csv.QUOTE_ALL)
    writeR.writerow(["Longform","Shortform","ID","Frequency","Standard Div","Average","Suspicious"])
    writeR.writerows(processed)

def grab_db_write_table(dbIn, tableIn, fileOut, abstractName, IDName):

    connIn = sqlite3.connect(dbIn)
    curseIn = connIn.cursor()
    curseIn.execute("SELECT " + abstractName + ", " + IDName + " FROM " + tableIn)
    input = curseIn.fetchall()
    processed = _process(input,0,1,":memory:","tab")
    out = open(fileOut, "w", newline = "")
    writeR = csv.writer(out, quoting = csv.QUOTE_ALL)
    writeR.writerow(["Longform","Shortform","ID","Frequency","Standard Div","Average","Suspicious"])
    writeR.writerows(processed)
    connIn.close()

def grab_table_write_db(fileIn, dbOut, tableOut, abstractName, IDName):
    readR = csv.reader(open(fileIn, newline = "")) # readR will be used to read fileIn row by row (make sure it is a csv)
    firstRow = next(readR) # make sure fileIn has headers as well
    searchIndex = firstRow.index(abstractName)
    IDIndex = firstRow.index(IDName) # use searchIndex and IDIndex as indices to search and ID respectively
    _process(readR,searchIndex,IDIndex,dbOut,tableOut)

def grab_db_write_db(dbIn, tableIn, dbOut, tableOut, abstractName, IDName):
    connIn = sqlite3.connect(dbIn)
    curseIn = connIn.cursor()
    curseIn.execute("SELECT " + abstractName + ", " + IDName + " FROM " + tableIn)
    input = curseIn.fetchall()
    _process(input,0,1,dbOut,tableOut)
    connIn.close()
