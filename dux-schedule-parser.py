# https://www.ssslsoftball.com/teams/default.asp?u=SOUTHSHORESUMMERSOFT&s=softball&p=schedule&format=List&d=ALL

# Parse the website and convert the schedule to a JSON data structure

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

# Get the website
url = 'https://www.ssslsoftball.com/teams/default.asp?u=SOUTHSHORESUMMERSOFT&s=softball&p=schedule&format=List&d=ALL'
response = requests.get(url)
html = response.content

# Parse the website
soup = BeautifulSoup(html, 'html.parser')
table = soup.find('table')

# Get the table headers
headers = table.find('thead').find_all('td')
header_names = []
for header in headers:
    header_names.append(header.text)


# Get the table rows
rows = table.find_all('tr')
data = []
the_date = ''
division = ''
for row in rows:
    if row.has_attr('class') and 'div2' in row['class']:
        the_date = row.find('td').text
        # convert the date from long format to short format
        dt = datetime.strptime(the_date, '%A, %B %d, %Y')

        # Convert the datetime object into a short format date string
        the_date = dt.strftime('%m/%d/%Y')

    elif row.has_attr('class') and 'div3' in row['class']:
        division = row.find('td').text 
    else:
        cells = row.find_all('td')
        if len(cells) > 1:
            game = {}
            for i in range(len(cells)):
                if '\u00a0' not in header_names[i]:
                    game[header_names[i]] = cells[i].text

                if 'Time' in header_names[i]:
                    game[header_names[i]] = re.sub(r'\s+', ' ', cells[i].text).strip()
                    
            
            game['Date'] = the_date
            game['Division'] = division
            
            # only append the game to data if the Home or Away team contains Duxbury
            if 'Duxbury' in game['Home'] or 'Duxbury' in game['Away']: data.append(game) 

# Sort the data by Duxbury Team, noting that Duxbury Team may show up in either the Away or Home columns
data = sorted(data, key=lambda x: x['Home'] if 'Duxbury' in x['Home'] else x['Away'])

# Convert the data to JSON
json_data = json.dumps(data, indent=4)
print(json_data)

# print the json out as a csv
for game in data:
    print(f"{game['Date']},{game['Time']},{game['Home']},{game['Away']},{game['Location']}, {game['Division']}")


# Write the JSON data to a file
with open('schedule.json', 'w') as file:
    file.write(json_data)

