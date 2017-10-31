# pycon_capture
Automated conference video capture and upload for PyconUK (and others)

## Session Metadata
The session metadata is obtained from the PyCon UK 2017 website repository on Github. The simplest way to do this is to clone the website repo and run `manage.py loadpages`, for example:

```
$ mkdir -p /usr/local/src/pycon/2017
$ cd /usr/local/src/pycon/2017
$ git clone https://github.com/PyconUK/2017.pyconuk.org pyconuk_website
$ cd pyconuk_website
$ python3 manage.py loadpages
```

This prepares the Sqlite database at
`/usr/local/src/pyconuk_website/db.sqlite3`

Note that Python 3.5+ is required, due to use of `django-amber` by the website. To avoid switching interpreter versions, the session metadata scripts also use Python 3.5+.

### Session Config
The session metadata scripts require a few external variables (like the location of the database), and these are stored in a yaml config file. If you clone the website to the directory suggested, then the default location value in the file will be correct, otherwise you will have to edit it.

To (re-)create the session config file, change to the `pycon_capture` directory and run
`python3 session_config.py`. This will create a fresh `session_config.yml` file that you can edit as needed.

The data fields stored in the file are
`conference_year` four digit year used for labelling video titles
`session_metadata_db` the file name `db.sqlite3`
`session_metadata_path` the absolute path to the metadata database file
`test_day` specify a two-digit, zero-padded day number to override ‘now’ for testing
`test_time`specify a zero-padded 24 hour time (example 09:30) to override ’now’ for testing
`video_title_prefix` a text prefix for labelling video titles (example ‘PYCON UK’)

### Fetching Session Metadata using the command line
You can fetch session metadata directly from the command line using 
`python3 get_session_metadata.py`

In the absence of any command line switches, this will fetch a list of all sessions in the database. The output is sorted by day number, then time within day, then room name within time. At present, if conference dates span a month end (example, 30, 31, 01, 02), then these will be sorted strictly numerically.

The available switches are
`-d --day` specify a day number, example 27
`-r --room` specify part of a room name, example ‘ferrier’, this is case insensitive
`-t --time` specify a time, example 11:23, this is normalised to the prior half hour, example 11:00
`-n --now` list sessions on now
`-p --prior` list prior sessions

The switches `-t -n -p` are mutually exclusive. Using now and prior will work from your current system clock time, unless you set `test_time` in the configuration file. Note that times are selected independently of days: if you don’t specify a day number, you will get all sessions ‘on now’ for all days in the conference. The time slot organisation currently works on a fixed half-hourly cycle.

The query will fetch all sessions that are _ongoing_ at the time specified. For example, giving a time of 11:30 will fetch a session running 09:30 - 12:00, as well as a session running 11:30 - 12:00. Note that, at 11:30, fetching ‘prior’ sessions will also return the session running 09:30 - 12:00, as this was running in the ‘prior’ slot of 11:00 - 11:30.

You can show all the available switches with `python3 get_session_metadata.py -h`

### Fetching Session Metadata from a script
To fetch session metadata using a script call, import the classes and call the class constructors:

```
from sessions import Session, Sessions
from session_config import SessionConfig

( ... other code ... )

sc = SessionConfig()
ss = Sessions(sc)
```
The `SessionConfig` object is arranged as a namespace. When called as part of `__main__` it combines the configuration file variables with the command line arguments. When called from a script, only the configuration file variables are relevant. The code above will fetch all sessions in the database, as it is not limited by day, room or time.

To filter the fetched sessions, like the command line switches, pass variables to the constructor. Fore example
`ss = Sessions(sc, day=28, room='room', start='11:30')`
will fetch all sessions running at 11:30 on the 28th in all rooms that include ‘room’ in their name. Note that it is currently not possible to specify ‘prior’ using a script call. You must always pass a valid SessionConfig object.

### Formatting metadata output
The default `str` output gives one item per output line, with just times, date, room, speaker and title. To get detailed output, use one of the following options:
`-l --long` list all fields down the page, with field names
`-b —-bare` list all fields down the page, without field names

From a script, use `ss.print_long()` and  `ss.print_bare()`

You can also access the list of Sessions and the Session objects directly to extract values.

### SQL queries
The two SQL queries used within the script are included in the `../sql/` directory. These can be pasted in to the [DB Browser for SQLite](http://sqlitebrowser.org/) and the search criteria edited directly as needed. The scripts have their own string representation, and do not need these external files.



