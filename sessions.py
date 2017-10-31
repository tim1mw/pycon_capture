import sqlite3
import os
import re

import timeslot
from session_config import SessionConfig

DAY_FROM_DATE_STRING = re.compile('[0-9]+')

FIELD_NAMES = {'title': 0, 'room': 1, 'name': 2, 'date': 3, 'start': 4, 'finish': 5, 
    'subtitle': 6, 'track': 7, 'video': 8, 'slides': 9, 'content': 10
}
ALL_SESSIONS_QUERY = '''
select ss.title, sl.room, sp.name, sl.date, min(sl.time) as start_time, max(sl.time) as finish_time,
ss.subtitle, ss.track, ss.video, ss.slides, ss.content
from pyconuk_session ss
inner join pyconuk_scheduleslot sl on sl.session_id = ss.id
inner join pyconuk_speaker sp on ss.speaker_id = sp.id
where sl.date like "%{0}%" and sl.room like "%{1}%"
group by ss.title
'''

TIMED_SESSIONS_QUERY = '''
select * from
(
select ss.title, sl.room, sp.name, sl.date, min(sl.time) as start_time, max(sl.time) as finish_time,
ss.subtitle, ss.track, ss.video, ss.slides, ss.content
from pyconuk_session ss
inner join pyconuk_scheduleslot sl on sl.session_id = ss.id
inner join pyconuk_speaker sp on ss.speaker_id = sp.id
where sl.date like "%{0}%" and sl.room like "%{1}%"
group by ss.title
) rs 
where rs.start_time <= "{2}" and rs.finish_time >= "{2}"
'''

def day_number_string(date_string):
    match = DAY_FROM_DATE_STRING.search(date_string)
    if match:
        return '{:0>2}'.format(match.group(0))
    else:
        return '00'

class Session():
    def __init__(self, db_fields, prefix='', year=''):

        def assign_field(field, default=''):
            if db_fields[FIELD_NAMES[field]]:
                self.__dict__[field] = db_fields[FIELD_NAMES[field]]
            else:
                self.__dict__[field] = default

        if prefix or year:
            video_prefix = prefix + ' ' + str(year) + ': '
        else:
            video_prefix = ''
        self.__dict__['talk_name'] = db_fields[FIELD_NAMES['title']]
        self.__dict__['video_name'] = video_prefix + self.talk_name
        self.__dict__['day'] = db_fields[FIELD_NAMES['date']]
        self.__dict__['room'] = db_fields[FIELD_NAMES['room']]
        self.__dict__['speaker'] = db_fields[FIELD_NAMES['name']]
        self.__dict__['start_time'] = timeslot.string_to_time(db_fields[FIELD_NAMES['start']])
        self.__dict__['start_time_string'] = timeslot.time_to_string(self.start_time)
        self.__dict__['finish_time'] = timeslot.string_to_time(db_fields[FIELD_NAMES['finish']], 30)
        self.__dict__['finish_time_string'] = timeslot.time_to_string(self.finish_time)
        self.__dict__['sort_key'] = day_number_string(self.day) + '-' + self.start_time_string + \
            '-' + self.finish_time_string + '-' + self.room
        assign_field('subtitle', 'No subtitle')
        assign_field('track', 'No track assigned')
        assign_field('video', 'No video link available')
        assign_field('slides', 'No slides link available')
        assign_field('content', 'No talk description available')

    def __str__(self):
        return '{} - {}  {:16} {:16} {:20} {} '.format(
            timeslot.time_to_string(self.start_time), timeslot.time_to_string(self.finish_time),
            self.day, self.room, self.speaker, self.video_name
            )

    def print_long(self):
        fields_to_print = ('day', 'start_time_string', 'room', 'speaker', 'talk_name', 'video_name', \
            'subtitle', 'track', 'video', 'slides', 'content' )
        lines = []
        for f in fields_to_print:
            add_newline = '\n' if f == 'content' else ''
            lines.append('{:20} : {}{}'.format(f, add_newline, self.__dict__[f]))
        lines.append('')
        return '\n'.join(lines)

    def print_bare(self):
        fields_to_print = ('day', 'start_time_string', 'room', 'speaker', 'talk_name', 'video_name', \
            'subtitle', 'track', 'video', 'slides', 'content' )
        lines = []
        for f in fields_to_print:
            lines.append('{}'.format(self.__dict__[f]))
        lines.append('')
        return '\n'.join(lines)


class Sessions():
    def __init__(self, config, day='', room='', start=''):
        self.c = config
        if day:
            self.c.day = day
        if room:
            self.c.room = room
        if start:
            self.c.time = start
        self.db_filename = os.path.join(self.c.session_metadata_path, self.c.session_metadata_db)
        if not os.path.isfile(self.db_filename):
            raise IOError("Could not find metadata database '{}'".format(self.db_filename))
        try:
            self.db_conn = sqlite3.connect(self.db_filename)
        except sqlite3.Error as e:
            raise IOError("Could not connect to metadata database: {}".format(e.args[0]))
        self.db_cursor = self.db_conn.cursor()
        try:
            if self.c.time == '':
                query_name = 'all sessions'
                self.db_cursor.execute(ALL_SESSIONS_QUERY.format(self.c.day, self.c.room))
            else:
                query_name = 'timed sessions'
                self.db_cursor.execute(TIMED_SESSIONS_QUERY.format(self.c.day, self.c.room, self.c.time))
        except sqlite3.Error as e:
            raise IOError("Could not execute sqlite '{}' query: {}".format(query_name, e.args[0]))
        self.sessions = []
        for row in self.db_cursor:
            self.sessions.append(Session(row, self.c.video_title_prefix, self.c.conference_year))
        self.sessions.sort(key=lambda session: session.sort_key)

    def __str__(self):
        lines = [str(s) for s in self.sessions]
        return '\n'.join(lines)

    def __iter__(self):
        for s in self.sessions:
            yield s

    def __len__(self):
        return len(self.sessions)

    def print_down(self, print_long):
        output = ''
        for s in self.sessions:
            if print_long:
                output += s.print_long()
            else:
                output += s.print_bare()
        return output

    def print_long(self):
        return self.print_down(True)

    def print_bare(self):
        return self.print_down(False)


if __name__ == '__main__':
    sc = SessionConfig()
    ss = Sessions(sc, '27', 'D', '14:30')
    print('length={}'.format(len(ss)))
    print(ss)
    for s in ss:
        print(s.print_long())
        print(s.print_bare())
    # ss = Sessions(sc, '27', '', '14:30')
    # print('length={}'.format(len(ss)))
    # print(ss)
    # for s in ss:
    #     print(s)
    # ss = Sessions(sc, '', 'D', '14:30')
    # print('length={}'.format(len(ss)))
    # print(ss)
    # for s in ss:
    #     print(s)
    # ss = Sessions(sc, '27', 'D', '')
    # print('length={}'.format(len(ss)))
    # print(ss)
    # for s in ss:
    #     print(s)
