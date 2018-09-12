import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path
import os
from os.path import isfile, join
import sqlite3


def get_talk_page(href):
    my_file = Path("files/"+href[15:19]+"_"+href[20:])
    if not my_file.is_file():
        print("files/"+href[15:19] +"_"+href[20:] + " New File")
        href_page = requests.get(base_url + href[:19])
        with open("files/"+href[15:19]+"_"+href[20:], 'w') as page:
            page.write(str(href_page.content))
        time.sleep(1)
    else:
        print("File: "+"files/"+href[15:19]+"_"+href[20:]+" exists. Skipping...")


def parse_talk_page(input_data, room):
    try:
        talk_page = BeautifulSoup(input_data, 'html.parser')
    except:
        print()

    title = talk_page.select('h1')[1].text.strip()
    subtitle = talk_page.select('h2.proposal-subtitle')

    # not all talks/workshops have a subtitle
    if subtitle == []:
        subtitle = "-"
    else:
        subtitle = subtitle[0].text

    authors = talk_page.select('p.proposal-names')  # string might contain more than 1 author
    if authors == []:
        authors = "-"
    else:
        authors = authors[0].text
    # TODO - seperate authors into list? - not needed for youtube copy pasta?
    # TODO - parse unicode chars - check how YT handles them

    slots = talk_page.select('p.proposal-slots')[0].text.replace('\\n', '\n').strip()

    # if contains >1 slot, is probably a workshop not a talk
    slot_list = []
    for line in slots.splitlines():

        # Slots String contains lots of whitespace including empty lines
        if not line.strip() == "":
            slot_list.append(line.strip())

    proposal_type = talk_page.select('div.proposal-type')

    # Things that are not talks or workshops are left blank (e.g Keynote)
    if proposal_type == []:
        proposal_type = "-"
    else:
        proposal_type = proposal_type[0].text

    list_of_abstract_paragraphs = []

    # Abstract doesnt have it's own class, so we grab all the ps between the 2 hrs
    for hr in talk_page.find_all("hr"):
        for item in hr.find_next_siblings():
            if item.name == "hr":
                break
            foo = item.find_all("p")  # item is a div, not a p, so search within
            if not foo == []:
                list_of_abstract_paragraphs = foo

    abstract_text = ""

    for p in list_of_abstract_paragraphs:
        abstract_text += p.get_text(separator="\n")  # converts line breaks to \n correctly
        abstract_text += "\n\n"  # preserve line spacing when pasting plain text

    # Beginning programmers and data scientist section
    difficulty_flags = ""
    ul = talk_page.select("ul")
    if len(ul) <2:
        ul = ""
    else:
        ul = ul[1].select("li") # list of <li>, (one or more)

        for li in ul:
            difficulty_flags += li.text
            difficulty_flags += "\n"

    # day_field =
    day_field = "Monday"

    # time_field
    time_field = "0900-1000"

    # room
    # room =  "" # room is not on talk page, only on schedule

    #print("**************")
    #print(file)
    #print(title)
    #print(subtitle)
    #print(authors)
    #print(slot_list)
    #print(proposal_type)
    #print(abstract_text)
    # print(ul)
    #if difficulty_flags:
    #    print(difficulty_flags.strip())

    return [file, title, subtitle, authors, room, day_field, time_field, slot_list, proposal_type, abstract_text, difficulty_flags.strip()]

print("Downloads PyconUK schedule page")
print("then downloads every talk page to its own file.")
print("Then we run beautifulsoup4 over the files to create a db")

time.sleep(3)

print("creating folder for talk pages")
if not os.path.exists("./files/"):
    os.makedirs("./files/")

time.sleep(1)


base_url = "https://2018.hq.pyconuk.org/"

page = requests.get(base_url+"schedule/")

print(page.status_code)
# print(page.content)

soup = BeautifulSoup(page.content, 'html.parser')

hrefs = []

# build list of hrefs
for td in soup.find_all('td', class_='selectable-schedule '):
    # td.find("a")
    room_name = td.find("span").text
    hrefs.append(td.find("a")['href']+(room_name.replace(" ","-")))
    print(td.find("a")['href']+(room_name.replace(" ","-")))
    # print(td.find("span").text)

deduped_hrefs = list(set(hrefs))  # converts to set and back to remove dupes (dupes are not talks?)

for item in deduped_hrefs:
    # print("item = " + item)
    get_talk_page(item)

onlyfiles = [f for f in os.listdir("files/") if isfile(join("files/", f))]

print("removing old db")
if isfile('mydb.db'):
    os.remove('mydb.db')

db = sqlite3.connect('mydb.db')

# Get a cursor object
cursor = db.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedule(id INTEGER PRIMARY KEY, 
    file TEXT,
    title TEXT,
    subtitle TEXT,
    authors TEXT,
    room TEXT,
    day_field TEXT,
    time_field TEXT,
    slot_list TEXT,
    proposal_type TEXT,
    abstract_text TEXT,
    difficulty_flags TEXT)
''')
db.commit()
#db.close()

for file in onlyfiles:
    with open("files/" + file, 'r') as data:
        #print(file)
        row = parse_talk_page(data, file[5:].replace("-"," "))
        print (file[5:].replace("-"," "))
        # TODO zip

        for slot in row[7]:
            cursor.execute('''INSERT INTO schedule(file, title,
                            subtitle, authors, room, day_field, time_field, slot_list, proposal_type, abstract_text, difficulty_flags)
                          VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (row[0], row[1],
                        row[2], row[3],
                        row[4], slot.split(",")[0],
                        slot.split(",")[1], "\n".join(row[7]),
                        row[8], row[9],
                        row[10]))


db.commit()
db.close()
