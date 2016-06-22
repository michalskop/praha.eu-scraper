# scrape representatives from praha.eu from a single vote event and save them in temp datafiles

import scrapeutils
from lxml import html, etree
import csv
import re

ve_id = 23698


outfile = open('tempdata/people_'+str(ve_id)+'.csv', 'w')
outwriter = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)

url = "http://www.praha.eu//jnp/cz/o_meste/primator_a_volene_organy/zastupitelstvo/vysledky_hlasovani/index.html?resolutionNumber=&printNumber=&s=1&meeting=&start=&votingId=" + str(ve_id)
domtree = html.fromstring(scrapeutils.download(url))
trs = domtree.xpath('//tbody/tr')

# for each person
for tr in trs:
    row = []
    tds = tr.xpath('td')
    row.append(re.search('memberId=(\d{1,})',tds[0].xpath('a/@href')[0]).group(1).strip())
    row.append(tds[0].xpath('a')[0].text.strip())
    outwriter.writerow(row)
outfile.close()
