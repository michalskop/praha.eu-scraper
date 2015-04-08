# scrape all votes from praha.eu and save them in temp datafiles

import scrapeutils
from lxml import html, etree
import math
import csv
import datetime
import re

terms = {
  #'1998-2002': 18280,
#  '2002-2006': 18281,
#  '2006-2010': 18282,
#  '2010-2014': 18284,
  '2014-2018': 29783,
}

for tkey in terms:
    outfileve = open('tempdata/vote_events-' + tkey + '.csv', 'w')
    outwriterve = csv.writer(outfileve, quoting=csv.QUOTE_NONNUMERIC)
    outfilev = open('tempdata/votes-' + tkey + '.csv', 'w')
    outwriterv = csv.writer(outfilev, quoting=csv.QUOTE_NONNUMERIC)
    
    # get number of pages
    url0 = 'http://www.praha.eu/jnp/cz/o_meste/primator_a_volene_organy/zastupitelstvo/vysledky_hlasovani/index.html?size=5&periodId=' + str(terms[tkey]) + '&resolutionNumber=&printNumber=&s=1&meeting=&start=0'
    domtree = html.fromstring(scrapeutils.download(url0,cache=False))
    tcount = domtree.xpath('//div[@class="pg-count"]/strong')[0].text.strip()
    npages = math.ceil(int(tcount)/500)  #500 is max per page
    n = 0

    # for each page in pagination
    for page in range(0,npages):
        url = 'http://www.praha.eu/jnp/cz/o_meste/primator_a_volene_organy/zastupitelstvo/vysledky_hlasovani/index.html?size=500&periodId=' + str(terms[tkey]) + '&resolutionNumber=&printNumber=&s=1&meeting=&start=' + str(page*500)
        domtree = html.fromstring(scrapeutils.download(url,cache=False))
        trs = domtree.xpath('//tbody/tr')
        
        # for each vote event
        for tr in trs:
            rowve = []
            tds = tr.xpath('td')
            try:
                rowve.append(tds[0].text.strip())
            except:
                rowve.append('')
            rowve.append(datetime.datetime.strptime(tds[1].text,"%d.%m.%Y").strftime("%Y-%m-%d"))
            try:
                rowve.append(tds[2].text.strip())
            except:
                rowve.append('')
            try:
                rowve.append(tds[3].text.strip())
            except:
                rowve.append('')    
            rowve.append(tds[4].xpath('a/@href')[0].strip())
            rowve.append(re.search('votingId=(\d{1,})',tds[4].xpath('a/@href')[0]).group(1).strip())
            
            urlve = 'http://www.praha.eu' + rowve[4]
            domtreeve = html.fromstring(scrapeutils.download(urlve,cache=False))
            print(str(n) + ":" + str(tcount) + ":" + rowve[5])
            
            ps = domtreeve.xpath('//span[@class="fine-color"]/..')
            for p in ps:
                chunks = etree.tostring(p).decode('utf-8').split('</span>')
                j = 0
                for chunk in chunks:
                    if j > 0:
                        rowve.append(re.search('^[^<&]*',chunk.strip()).group(0))
                    j = j + 1
            
            outwriterve.writerow(rowve)
            
            trsve = domtreeve.xpath('//tbody/tr')
            for trve in trsve:
                rowv = []
                tdsv = trve.xpath('td')
                rowv.append(rowve[5])
                rowv.append(tdsv[0].xpath('a')[0].text.strip())
                rowv.append(re.search('memberId=(\d{1,})',tdsv[0].xpath('a/@href')[0]).group(1).strip())
                rowv.append(tdsv[1].text.strip())
                outwriterv.writerow(rowv)
            
            #raise(Exception)
            n = n + 1
 
    outfileve.close()
    outfilev.close()  
    #raise(Exception)
