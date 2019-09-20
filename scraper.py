"""Scrapes vote events from praha.eu and updates github datapackage."""

import csv
from datapackage import Package  # v0.8.3
import git

import praha_eu_utils as utils
import settings

terms = {
    # '1998-2002': 18280,
    #  '2002-2006': 18281,
    #  '2006-2010': 18282,
    #  '2010-2014': 18284,
    # '2014-2018': 29783,
    '2018-2022': 33394
}

resources_attributes = {
    "vote_events": ['id', 'start_date', 'motion:name', 'motion:number', 'motion:document', 'sources:link:url', 'legislative_session_id', 'result', 'counts:option:yes', 'counts:option:no', 'counts:option:abstain', 'number_of_people', 'present', 'identifier'],
    "voters": ['id', 'name', 'party', 'email'],
    "votes": ['vote_event_id', 'voter_id', 'option']
}

path = "data/"  # from this script to datapackage.json

# repo settings
repo = git.Repo(settings.git_dir)
git_ssh_identity_file = settings.ssh_file
o = repo.remotes.origin
git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file

for term in terms:
    ves_table = []
    votes_table = []
    voters_table = []
    ves_ids = []
    voters_ids = []
    ves_dict = {}
    voters_dict = {}
    numbers = {
        "vote_events": 0,
        "voters": 0,
        "votes": 0
    }
    # get datapackage from github
    datapackage_url = "https://raw.githubusercontent.com/michalskop/praha.eu-scraper/master/data/" + term + "/datapackage.json"
    dp = Package(datapackage_url)

    # get all vote events
    ves = utils.get_all_vote_events(terms[term])

    # get all vote_event_ids from dp and from ves, get links to ves
    dp_ves_ids = []
    for row in dp.get_resource('vote_events').read(keyed=True):
        dp_ves_ids.append(int(row['id']))
        ves_table.append(row)

    for row in ves:
        ves_ids.append(int(row['id']))
        ves_dict[row['id']] = row

    # prepare existing votes
    for row in dp.get_resource('votes').read(keyed=True):
        votes_table.append(row)

    # download vote event if not exists in dp
    for ve_id in sorted(ves_ids):
        if ve_id not in dp_ves_ids:
            ve = utils.get_vote_event(ves_dict[str(ve_id)]['sources:link:url'], ve_id)
            ves_dict[ve_id] = ves_dict[str(ve_id)].update(ve['vote_event'])
            ves_table = ves_table + [ves_dict[str(ve_id)]]
            numbers['vote_events'] += 1
            votes_table = votes_table + ve['votes']
            numbers['votes'] += len(ve['votes'])

    # update voters
    for row in dp.get_resource('voters').read(keyed=True):
        voters_dict[row['id']] = row
        voters_ids.append(int(row['id']))
    current_voters = utils.get_current_voters()
    for current_person in current_voters:
        try:
            voters_dict[int(current_person['id'])]
        except Exception:
            voters_ids.append(int(current_person['id']))
            numbers['voters'] += 1
        voters_dict[int(current_person['id'])] = current_person
    for person_id in sorted(voters_ids):
        try:
            voters_table.append(voters_dict[person_id])
        except Exception:
            try:
                voters_table.append(voters_dict[person_id])
            except Exception:
                print(person_id)

    # save CSVs
    tables = {
        'voters': voters_table,
        'votes': votes_table,
        'vote_events': ves_table
    }
    # bots text for commit
    happy_text = ''
    for k in numbers:
        # if numbers[k] > 0:
            happy_text += ", " + str(numbers[k]) + " " + k
    for k in resources_attributes:
        for resource in dp.resources:
            if resource.descriptor['name'] == k:
                with open(settings.git_dir + path + term + '/' + resource.descriptor['path'], "w") as fout:
                    fieldnames = resources_attributes[k]
                    csvdw = csv.DictWriter(fout, fieldnames)
                    csvdw.writeheader()
                    for row in tables[k]:
                        csvdw.writerow(row)
                a = repo.git.add(settings.git_dir + path + term + '/' + resource.descriptor['path'])
    with repo.git.custom_environment(GIT_COMMITTER_NAME=settings.bot_name, GIT_COMMITTER_EMAIL=settings.bot_email):
        repo.git.commit(message="happily updating data %s%s" % (term, happy_text), author="%s <%s>" % (settings.bot_name, settings.bot_email))
    with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        o.push()
    # message="happily updating data %s%s" % (term, happy_text)
