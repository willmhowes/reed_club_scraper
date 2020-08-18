from bs4 import BeautifulSoup
import requests
import json
import re

def get_page(url, url_mod):
    response = requests.get(url + url_mod, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")
    header = content.find('main').find('p')
    return response, content, header

def count_clubs(header):
    # locate total number of clubs
    total_clubs = re.findall('([0-9]+) matching', header.get_text())[0]
    # calculate last club loaded
    last_shown = header.find_all('strong')[1].get_text()
    return int(last_shown), int(total_clubs)

output = 'clubdata.json'

url = 'https://www.reed.edu/student-engagement/student-org-search/'
url_mod = 'index.php?submit=Search'

club_list = []

total_clubs = 1
last_shown = 0

# while next page exists
while last_shown < total_clubs:
    # GET HTML
    response, content, header = get_page(url, url_mod)

    # update club counters and locate club table
    last_shown, total_clubs = count_clubs(header)
    table = content.find('table')

    # parse club table
    for row in table.find_all('tr')[1:]: # first row contains headers
        columns = row.find_all('td')
        name = columns[0].get_text()
        desc = columns[1].get_text()[:-10] # final chars are garbage

        club = {
            "name" : name,
            "description" : desc
        }
        club_list.append(club)

    # update url_mod for next page load
    url_mod = 'index.php?start=' + str(last_shown + 1) + '&submit=Search'

# write data to json file
with open(output, 'w') as outfile:
    json.dump(club_list, outfile)
