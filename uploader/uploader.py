from tkinter import *
import tkinter as tk
from tkinter.filedialog import askopenfilename
import sqlite3

root = Tk()

def button_pushed():
    print("button")
    filename = askopenfilename()
    print(filename)
    filename_text.delete(1.0, END)
    filename_text.insert(END, filename)


def callback(*args):

    #print(args)
    #print(args[0])

    # fires as the vars are being set up, so 'day' will fire before 'talk' exists.
    # we don't care about them until they are all inited, so skip accessing them until they all exist
    try:
        current_state['day'] = dropdown1_var.get()
        current_state['room'] = dropdown2_var.get()
        current_state['talk'] = dropdown3_var.get()
        foo = type(dropdown3)
    except:
        current_state['day'] = ""
        current_state['room'] = ""
        current_state['talk'] = ""
        return # do nothing until everything has been intited

    print("*** State change ***")
    print("Day: " + current_state['day'])
    print("Room: " + current_state['room'])
    print("Talk: " + current_state['talk'])

    parsed_day = "'"+current_state['day']+"'"
    parsed_room = "'"+current_state['room']+"'"
    parsed_talk = "'"+current_state['talk']+"'"

    #print(parsed_day+" "+ parsed_room)
    # TODO escape special characters in parameters
    possible_talks = cursor.execute(f"SELECT DISTINCT title FROM schedule WHERE day_field ={parsed_day} AND room ={parsed_room}").fetchall()

    possible_talk_list = []
    for item in possible_talks:
        possible_talk_list.append(item[0])

    print("Possible talks: "+str(possible_talks))

    # Clear dropdown
    dropdown3['menu'].delete(0, 'end')

    # Insert list of new options (tk._setit hooks them up to var)
    for talk in possible_talk_list:
        dropdown3['menu'].add_command(label=talk, command=tk._setit(dropdown3_var, talk))

    if possible_talk_list == []:
        possible_talk_list = ["-"]

    # if current_state[talk] is a member of possible talks, replace list, but set entry to current_state[talk]
    if current_state['talk'] in possible_talk_list:
        # TODO talks that have multiple entries might have problems (eg lightning talks)
        pass
    else:
        dropdown3_var.set(possible_talk_list[0])

    # Now we fill the text boxes

    selected_metadata_raw = cursor.execute(f"SELECT *  FROM schedule WHERE day_field ={parsed_day} AND room ={parsed_room} AND title ={parsed_talk}").fetchall()

    print(selected_metadata_raw)
    if selected_metadata_raw == []:
        first_row_list = []
        print("*** NO MATCHING TALKS ***")
        # TODO investigate why we get here
        return
    else:
        first_row_list = list(selected_metadata_raw[0])

    # print("Meta: " + str(selected_metadata_raw))
    # print("list(Meta[0]): " + str(list(selected_metadata_raw[0])))
    # print("Type of Meta[0]: " + str(type(selected_metadata_raw[0])))

    # row format: ID, filename, title, subtitle, author, room, day, time, slot list, proposal type, abstract, difficulty flags.

    # Youtube description will be
    # subtitle
    # author
    # abstract
    # difficulty flags

    # gab title from current state
    title.delete(1.0, END)
    title.insert(END, current_state['talk'])

    # check for uniquness of record?
    if len(selected_metadata_raw) > 1:
        print("*** MULTIPLE RECORDS MATCH - USING FIRST ONE***")
    elif len(selected_metadata_raw) == 0:
        print("*** ZERO RECORDS MATCH ***")

    description_string = ""
    #subtitle
    if first_row_list[3] == "-":
        pass
    else:
        description_string += first_row_list[3]+"\n\n"

    #author
    if first_row_list[4] == "-":
        pass
    else:
        description_string += "Presenter(s): "+first_row_list[4] + "\n\n"

    #abstract
    description_string += first_row_list[10]

    #difficulty lags
    description_string += first_row_list[11]

    T.delete(1.0, END)
    T.insert(END, description_string)


def upload():
    print("*** ATTEMPTING TO UPLOAD ***")

    print("piecing together params")

    # TODO - exec this
    # TODO be mindfull of escaping special chars
'''
 youtube-upload \
  --title="A.S. Mutter" 
  --description="A.S. Mutter plays Beethoven" \
  --tags="python, programming, pycon, pyconuk" \
  --default-language="en" \
  --default-audio-language="en" \
  --client-secrets=my_client_secrets.json \
  --credentials-file=my_credentials.json \
  --private\
  <path/filename>
'''

db = sqlite3.connect('mydb.db')
cursor = db.cursor()

current_state = {
  "day": "",
  "room": "",
  "talk": ""
}
day_tuples = set(cursor.execute('SELECT day_field FROM schedule').fetchall())

day_list = []
for item in day_tuples:
    day_list.append(item[0])

day_list.sort(key = lambda x: x.split(" ")[-1]) # split by space, then sort by last field (ie day number)
print(day_list)

room_tuples = set(cursor.execute('SELECT room FROM schedule').fetchall())

room_list = []
for item in room_tuples:
    room_list.append(item[0])

room_list.sort()
print(room_list)

talk_tuples = set(cursor.execute('SELECT title FROM schedule').fetchall()) # will include dupes

talk_list = []
for item in talk_tuples:
    talk_list.append(item[0])

talk_list.sort()
print(talk_list)

# not realy needed, but helps mental model.
DAY_OPTIONS = day_list
ROOM_OPTIONS = room_list
TALK_OPTIONS = talk_list

dropdown1_var = StringVar(root)
dropdown1_var.trace("w", callback)
dropdown1_var.set(DAY_OPTIONS[0]) # default value
current_state['day'] = DAY_OPTIONS[0]

dropdown1 = OptionMenu(root, dropdown1_var, *tuple(DAY_OPTIONS))
#dropdown1 = apply(OptionMenu, (root, dropdown1_var) + tuple(DAY_OPTIONS))
dropdown1.pack()

dropdown2_var = StringVar(root)
dropdown2_var.trace("w", callback)
dropdown2_var.set(ROOM_OPTIONS[0]) # default value
current_state['room'] = ROOM_OPTIONS[0]

dropdown2 = OptionMenu(root, dropdown2_var, *tuple(ROOM_OPTIONS))
dropdown2.pack()

dropdown3_var = StringVar(root)
dropdown3_var.trace("w", callback)
#dont set default value
#dropdown3_var.set(TALK_OPTIONS[0]) # default value
#current_state['talk'] = TALK_OPTIONS[0]

dropdown3 = OptionMenu(root, dropdown3_var, *tuple(TALK_OPTIONS))
dropdown3.pack()

title = Text(root, height=2, width=200, wrap=WORD)
title.pack()

T = Text(root, height=20, width=200, wrap=WORD)
T.pack()
quote = """Example Abstract: This is an example abstract that
will be displayed by default if there is no database"""

title.insert(END, "Test title")
T.insert(END, quote)

filename_text = Text(root, height=2, width=200, wrap=WORD)
filename_text.pack()

filename_text.insert(END, "video.mp4")

b = Button(root, text="File Picker", command=button_pushed)
b.pack()

u = Button(root, text="Upload", command=upload)
u.pack()

callback("lol")

mainloop()