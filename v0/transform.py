# transform data from temp datafiles to csv / popolo specification

import csv
import operator

terms = [
#  '1998-2002',
#  '2002-2006',
#  '2006-2010',
#  '2010-2014',
  '2014-2018'
]

def result2result(res):
    if res == 'Ano':
        return 'pass'
    if res == 'Ne':
        return 'fail'
    return ''

def option2option(o):
    if o == 'pro':
        return 'yes'
    if o == 'proti':
        return 'no'
    if o == 'zdržel se':
        return 'abstain'
    if o == 'chyběl':
        return 'absent'
    return 'not voting'

for term in terms:
    #vote event
    li = []
    r = ['identifier','start_date','motion:name','motion:number','sources:link:url', 'motion:document','legislative_session_id','result', 'counts:option:yes','counts:option:no','counts:option:abstain','number_of_people','present']
    with open('tempdata/vote_events-'+term+'.csv','r') as f:
        outfileve = open('data/vote_events-' + term + '.csv', 'w')
        outwriterve = csv.writer(outfileve, quoting=csv.QUOTE_NONNUMERIC)
        outwriterve.writerow(r)
        
        csvreader = csv.reader(f)
        for row in csvreader:
            r = [row[5],row[1],row[3],row[0],row[2],'http://www.praha.eu'+row[4],row[6]]
            try:
                r.append(result2result(row[7]))
                r = r + [row[8],row[9],row[10],row[11],row[12]]
            except:
                nothing = True
            li.append(r)
        out = sorted(li, key=operator.itemgetter(1))
        for r in out:
            outwriterve.writerow(r)

            #raise(Exception)
    #vote
    r = ['vote_event_id','voter_id','option']
    with open('tempdata/votes-'+term+'.csv','r') as f:
        outfilev = open('data/votes-' + term + '.csv', 'w')
        outwriterv = csv.writer(outfilev, quoting=csv.QUOTE_NONNUMERIC)
        outwriterv.writerow(r)
        
        csvreader = csv.reader(f)
        for row in csvreader:
            r = [row[0],row[2],option2option(row[3])]
            outwriterv.writerow(r)
    
    outfileve.close()
    outfilev.close()
