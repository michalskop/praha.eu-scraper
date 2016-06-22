# Voting records from Prague Assembly

Scraper and data of Prague Assembly (Praha.eu).

Contains data from roll-call votes in the Prague Assembly in tabular datapackage format (http://frictionlessdata.io/guides/tabular-data-package/) using Popolo standard (http://popoloproject.com/). The data are updated once a day.

## Example - the data from 2014-2018 term
http://data.okfn.org/tools/view?url=https%3A%2F%2Fraw.githubusercontent.com%2Fmichalskop%2Fpraha.eu-scraper%2Fmaster%2Fdata%2F2014-2018%2Fdatapackage.json

## Custom installation
Requirements:
- Python 3
- Python packages: csv, datetime, datapackage, gitPython, lxml, math, re, requests

Copy example settings into settings and correct it for your Github account (e.g., your bot's account)

    cp settings-example.py settings.py

Note: The origin for the local git project must be 'ssh' address (not 'https' one).

You can automate the data retrieval using cron.
