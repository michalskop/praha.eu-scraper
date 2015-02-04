# scrape current representatives from praha.eu and save them in temp datafiles

import scrapeutils
from lxml import html, etree
import csv

outfile = open('tempdata/current_people.csv', 'w')
outwriter = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)

url = "http://www.praha.eu/jnp/cz/o_meste/primator_a_volene_organy/zastupitelstvo/seznam_zastupitelu/index.html?size=100"
domtree = html.fromstring(scrapeutils.download(url))
trs = domtree.xpath('//tbody/tr')

# for each person
for tr in trs:
    row = []
    tds = tr.xpath('td')
    row.append(re.search('memberId=(\d{1,})',tds[0].xpath('a/@href')[0]).group(1).strip())
    row.append(tds[0].xpath('a')[0].text.strip())
    try:
        row.append(tds[1].text.strip())
    except:
        row.append('')
    row.append(tds[2].xpath('a')[0].text.strip())
    outwriter.writerow(row)
    
