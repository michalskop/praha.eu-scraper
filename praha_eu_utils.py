# utils for praha.eu scraper

# import csv
import datetime
# import json
from lxml import html, etree
import math
# import os
import re
import requests
# from urllib.parse import urlparse

def get_current_people():
    url = "http://www.praha.eu/jnp/cz/o_meste/primator_a_volene_organy/zastupitelstvo/seznam_zastupitelu/index.html?size=100"
    r = requests.get(url)
    if r.status_code == 200:
        domtree = html.fromstring(r.text)
        trs = domtree.xpath('//tbody/tr')

        # for each person
        people = []
        for tr in trs:
            person = {}
            tds = tr.xpath('td')
            person['id'] = re.search('memberId=(\d{1,})',tds[0].xpath('a/@href')[0]).group(1).strip()
            person['name'] = tds[0].xpath('a')[0].text.strip()
            try:
                person['party'] = tds[1].text.strip()
            except:
                person['party'] = ''
            person['email'] = tds[2].xpath('a')[0].text.strip()
            people.append(person)
        return people
    else:
        raise(Exception)

def result2result(r):
    if r == 'Ne':
        return 'fail'
    else:
        return 'pass'

def option2option(o):
    if o == 'pro':
        return 'yes'
    if o == 'proti':
        return 'no'
    if o == 'zdržel se':
        return 'abstain'
    if o == 'nehlasoval':
        return 'not voting'
    if o == 'chyběl':
        return 'absent'
    raise(Exception)

def get_vote_event(url,ve_id):
    print(ve_id)
    ve = {}
    attributes = ['legislative_session_id','result','counts:option:yes','counts:option:no', 'counts:option:abstain','number_of_people','present']
    r = requests.get(url)
    if r.status_code == 200:
        domtree = html.fromstring(r.text)
        ps = domtree.xpath('//span[@class="fine-color"]/..')
        i = 0
        for p in ps:
            chunks = etree.tostring(p).decode('utf-8').split('</span>')
            j = 0
            for chunk in chunks:
                if j > 0:
                    if i == 1:
                        ve[attributes[i]] = result2result(re.search('^[^<&]*',chunk.strip()).group(0))
                    else:
                        ve[attributes[i]] = re.search('^[^<&]*',chunk.strip()).group(0)
                    i = i + 1
                j = j + 1

        votes = []
        people = []
        trs = domtree.xpath('//tbody/tr')
        for tr in trs:
            vote = {}
            person = {}
            tds = tr.xpath('td')
            person['name'] = tds[0].xpath('a')[0].text.strip()
            person['id'] = re.search('memberId=(\d{1,})',tds[0].xpath('a/@href')[0]).group(1).strip()
            vote['voter_id'] = person['id']
            vote['option'] = option2option(tds[1].text.strip())
            vote['vote_event_id'] = str(ve_id)
            people.append(person)
            votes.append(vote)
        return {'vote_event': ve, 'votes': votes, 'people': people}
    else:
        raise(Exception)


def get_all_vote_events(period_id):
    url0 = 'http://www.praha.eu/jnp/cz/o_meste/primator_a_volene_organy/zastupitelstvo/vysledky_hlasovani/index.html?size=5&periodId=' + str(period_id) + '&resolutionNumber=&printNumber=&s=1&meeting=&start=0'
    r = requests.get(url0)
    vote_events = []
    if r.status_code == 200:
        domtree = html.fromstring(r.text)
        tcount = domtree.xpath('//div[@class="pg-count"]/strong')[0].text.strip()
        npages = math.ceil(int(tcount)/500)  #500 is max per page
        n = 0
        print("n pages:" + str(npages))

        # for each page in pagination
        for page in range(0,npages):
            url = 'http://www.praha.eu/jnp/cz/o_meste/primator_a_volene_organy/zastupitelstvo/vysledky_hlasovani/index.html?size=500&periodId=' + str(period_id) + '&resolutionNumber=&printNumber=&s=1&meeting=&start=' + str(page*500)
            rr = requests.get(url)
            if rr.status_code == 200:
                domtree = html.fromstring(rr.text)
                trs = domtree.xpath('//tbody/tr')
                # for each vote event
                for tr in trs:
                    ve = {}
                    tds = tr.xpath('td')
                    try:
                        ve['motion:number'] = tds[0].text.strip()
                    except:
                        ve['motion:number'] = ''
                    ve['start_date'] = datetime.datetime.strptime(tds[1].text,"%d.%m.%Y").strftime("%Y-%m-%d")
                    try:
                        ve['motion:document'] = tds[2].text.strip()
                    except:
                        ve['motion:document'] = ''
                    try:
                        ve['motion:name'] = tds[3].text.strip()
                    except:
                        ve['motion:name'] = ''
                    ve['sources:link:url'] = 'http://www.praha.eu' + tds[4].xpath('a/@href')[0].strip()
                    ve['id']  = re.search('votingId=(\d{1,})',tds[4].xpath('a/@href')[0]).group(1).strip()
                    ve['identifier'] = ve['id']
                    vote_events.append(ve)
            else:
                raise(Exception)
    else:
        raise(Exception)
    return vote_events
