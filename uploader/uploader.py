from tkinter import *
import tkinter as tk
from tkinter.filedialog import askopenfilename
import sqlite3
import os
import argparse

root = Tk()


def button_pushed():
    print("button")
    filename = askopenfilename()
    print(filename)
    filename_text.delete(1.0, END)
    filename_text.insert(END, filename)


def callback(*args):

    #print(args)
    # print(args[0])

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
        return  # do nothing until everything has been intited

    if args[-1] == "no_value" or args[-1] == "w": # if we didn't get a parameter proceed with defaults
        print("args to callback: "+args[-1])

    else: # else change state to passed param
        passed_param = cursor.execute(f"SELECT *  FROM schedule WHERE file LIKE '{args[-1].upper()}%'").fetchall()
        print("Passed param entry: "+ str(passed_param[0]))

        inputed_list = []
        for param in passed_param[0]:  # first row of returned possibilities
            inputed_list.append(param)
        print("input list: "+str(inputed_list))
        current_state['day'] = inputed_list[6]
        current_state['room'] = inputed_list[5]
        current_state['talk'] = inputed_list[2]

    print("*** State change ***")
    print("Day: " + current_state['day'])
    print("Room: " + current_state['room'])
    print("Talk: " + current_state['talk'])

    parsed_day = "'"+current_state['day']+"'"
    parsed_room = "'"+current_state['room']+"'"
    parsed_talk = current_state['talk'].replace("'", "''")
    parsed_talk = "'"+parsed_talk+"'"

    # print(parsed_day+" "+ parsed_room)

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
        # passes param doesnt rigger event in the same way - set dropdown explicitly
        dropdown3_var.set(possible_talk_list[possible_talk_list.index(current_state['talk'])])
        # dropdown3_var.set(possible_talk_list[0]) # find which entry current state talk is
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
        --default-language="en" --default-audio-language="en" \
        --client-secrets=my_client_secrets.json \
        --credentials-file=my_credentials.json \
        --private\
        <path/filename>
    '''

    new_title = title.get(1.0, END)
    file_name = filename_text.get(1.0, END)

    abstract = T.get(1.0, END)

    with open('description.txt', 'w') as file:  # Use file to refer to the file object

        file.write(abstract.strip("\n"))

    function_call = ""
    function_call += "c:\\Users\\Glen\\Documents\\git_repos\\youtube-upload\\bin\\youtube-upload.bat "
    #function_call += 'youtube-upload '
    function_call += '--title="'+new_title[:-1]+'" ' # added so apostrophe can be present - trim last newline

    function_call += '--client-secrets=C:\\Users\\Glen\\Documents\\git_repos\\client_id.json '
    # apostrophes can be present, need to test newlines and slashes
    function_call += '--description="$(< description.txt)" '
    #function_call += '--description="' + abstract.strip("\n") + '" '
    function_call += '--tags="python, programming, pycon, pyconuk" '
    function_call += '--default-language="en" --default-audio-language="en" '

    #function_call += '--client-secrets=my_client_secrets.json '


    #function_call += '--credentials-file=my_credentials.json '

    function_call += '--privacy private '
    function_call += file_name

    print(function_call)
    os.system(function_call)

def upload_program(ical_param, filename_param):

    global db
    #check for existance of db file
    if os.path.isfile('mydb.db'):
        db = sqlite3.connect('mydb.db')
    else:
        print("ERROR: expected mydb.db to be in the same folder as this script - Need to move it from where web_scraper created it")
    global cursor
    cursor = db.cursor()

    global current_state
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

    global dropdown1_var
    dropdown1_var = StringVar(root)
    dropdown1_var.trace("w", callback)
    dropdown1_var.set(DAY_OPTIONS[0]) # default value
    current_state['day'] = DAY_OPTIONS[0]

    global dropdown1
    dropdown1 = OptionMenu(root, dropdown1_var, *tuple(DAY_OPTIONS))
    #dropdown1 = apply(OptionMenu, (root, dropdown1_var) + tuple(DAY_OPTIONS))
    dropdown1.pack()

    global dropdown2_var
    dropdown2_var = StringVar(root)
    dropdown2_var.trace("w", callback)
    dropdown2_var.set(ROOM_OPTIONS[0]) # default value
    current_state['room'] = ROOM_OPTIONS[0]

    global dropdown2
    dropdown2 = OptionMenu(root, dropdown2_var, *tuple(ROOM_OPTIONS))
    dropdown2.pack()

    global dropdown3_var
    dropdown3_var = StringVar(root)
    dropdown3_var.trace("w", callback)
    #dont set default value
    #dropdown3_var.set(TALK_OPTIONS[0]) # default value
    #current_state['talk'] = TALK_OPTIONS[0]

    global dropdown3
    dropdown3 = OptionMenu(root, dropdown3_var, *tuple(TALK_OPTIONS))
    dropdown3.pack()

    global title
    title = Text(root, height=2, width=200, wrap=WORD)
    title.pack()

    global T
    T = Text(root, height=20, width=200, wrap=WORD)
    T.pack()
    quote = """Example Abstract: This is an example abstract that
    will be displayed by default if there is no database"""

    title.insert(END, "Test title")
    T.insert(END, quote)

    global filename_text
    filename_text = Text(root, height=2, width=200, wrap=WORD)
    filename_text.pack()

    filename_text.insert(END, filename_param)

    b = Button(root, text="File Picker", command=button_pushed)
    b.pack()

    u = Button(root, text="Upload", command=upload)
    u.pack()

    callback(ical_param)

    mainloop()


if __name__ == '__main__':

    #if called by another scipt, should be provided with a file and an ical entry
    parser = argparse.ArgumentParser()
    parser.add_argument("--ical_param")
    parser.add_argument("--filename_param")
    args = parser.parse_args()

    if args.filename_param:
        filename_param = args.filename_param
    else:
        #filename_param = "talk_video.mp4"
        filename_param ="C:/Users/Glen/Documents/git_repos/sample.m4v"

    if args.ical_param:
        ical_param = args.ical_param
    else:
        #ical_param = "no_value"
        ical_param = "0b96" # lightning talks
        upload_program(ical_param, filename_param)
