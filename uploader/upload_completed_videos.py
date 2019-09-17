import argparse
import requests
import sys
import os
import fnmatch
import re
import upload_one_video as uv
import socket

SIMPLE_HTML_TAG_RE = re.compile('<.*?>')
COMMON_KEYWORDS = ['python', 'programming', 'pycon', 'pyconuk']
VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')

READY_FOR_UPLOAD = 'ready_for_upload'
COULD_NOT_START_UPLOAD = 'could_not_start_upload'
COMPLETED_UPLOAD = 'completed_upload'
FAILED_UPLOAD = 'failed_upload'
VIDEO_SERVICE_AUTH = 'auth'

# TODO: Read all configuration details from this file
CONFIG_HOME = '.pycon_capture'
CONFIG_FILE = 'pycon_capture.yml'

# TODO: All these constants need to be read from the configuration file above
SCHEDULE_URL = 'https://pretalx.com/pyconuk-2019/schedule/export/schedule.json' # formerley 'https://2018.hq.pyconuk.org/schedule/json/'
VIDEO_FILE_ROOT = '/usr/local/src/pycon/videos'
VIDEO_FILE_EXTENSION = 'mp4'


def remove_html_tags(raw_text):
    clean_text = re.sub(SIMPLE_HTML_TAG_RE, '', raw_text)
    if clean_text != raw_text:
        # debugging only
        found_one = True
    return clean_text


def convert_newlines(multi_line):
    # Assume that if the text uses Mac old-style '\r' newlines, then there will be at least one '\r\r' sequence to find
    if multi_line.find('\r\r') > -1:
        # Mac old-style
        while '\r' in multi_line:
            multi_line = multi_line.replace('\r', '\n')
    else:
        # Windows
        while '\r\n' in multi_line:
            multi_line = multi_line.replace('\r\n', '\n')
    return multi_line


def squash_empty_lines(multi_line):
    # Get rid of unnecessary multiple blank lines, but keep one 'white space' separator
    while '\n\n\n' in multi_line:
        multi_line = multi_line.replace('\n\n\n', '\n\n')
    return multi_line


def all_text_cleaning(raw_text):
    return squash_empty_lines(convert_newlines(remove_html_tags(raw_text)))


class YTSessionData:
    '''
    This class only exists because the original upload script passed the parsed arg object into the function.
    Rather than rewrite that code now, create an object that has the same members.
    '''
    def __init__(self, filename, category, privacy, metadata):
        self.file = filename
        # Comma separated list
        self.keywords = metadata['keywords']
        self.title = metadata['title']
        self.description = metadata['description']
        self.category = category
        self.privacyStatus = privacy


class ScheduleData:
    def __init__(self):
        self.raw_schedule = self.read_schedule_data()
        self.parsed_schedule = self.parse_schedule_data()
        self.iterate_keys = None
        self.current_key_index = -1
        self.max_key_index = -1

    def __iter__(self):
        self.iterate_keys = list(self.parsed_schedule.keys())
        self.current_key_index = -1
        self.max_key_index = len(self.iterate_keys) - 1
        return self

    def __next__(self):
        if self.current_key_index < self.max_key_index:
            self.current_key_index += 1
            return self.iterate_keys[self.current_key_index]
        else:
            raise StopIteration

    def captive_portal(self):
        r = requests.get(SCHEDULE_URL, allow_redirects=False)

        if r.status_code == '302':  # redirect implies captive portal
            return True
        else:
            return False



    def read_schedule_data(self):

        if self.captive_portal():
            # launch browser to click through captive portal
            print("ERROR: REIDRECT DETECTED -- CONNECT TO CAPTIVE PORTAL AND RE-RUN SCRIPT")
            sys.exit(-2)
        else:
            r = requests.get(SCHEDULE_URL)

        try:
            the_schedule = r.json()
        except ValueError:
            print('Could not read the json schedule from {}'.format(SCHEDULE_URL))
            sys.exit(1)
        return the_schedule

    def parse_schedule_data(self):
        # We don't need to parse these, but leave the code in case we want it later
        # def get_times(raw_times):
        #     t_lookup = {}
        #     for time_number in range(len(raw_times)):
        #         t_lookup[time_number] = raw_times[time_number]
        #     return t_lookup
        #
        # def get_rooms(raw_rooms):
        #     r_lookup = {}
        #     for room_number in range(len(raw_rooms)):
        #         r_lookup[room_number] = raw_rooms[room_number]
        #     return r_lookup

        def interesting_event(one_event):
            try:
                if not one_event:
                    return False
                elif one_event['break_event']:
                    return False
                elif not one_event['id']:
                    return False
                else:
                    return True
            except IndexError:
                return False

        def list_of_speakers(one_event):
            string_of_speakers = ''

            for person in one_event["persons"]:
                for day in days:
                    for room in day["rooms"].values():
                        for event in room:
                            for person in event["persons"]:
                                string_of_speakers += person["public_name"] + ", "
            return string_of_speakers[:-2] # slice to remove the ", " from the last name in the list


        def parse_one_event(one_day, one_event):
            parsed_event = {
                'id': one_event.get('id', ''), # could also use 'guid'
                'title': one_event.get('title', ''),
                'speaker': list_of_speakers(one_event),  # speaker is a list of speaker objects parsed elsewhere.
                'subtitle': one_event.get('subtitle', ''),
                #'new_programmers': one_event.get('aimed_at_new_programmers', ''), #not present
                #'teachers': one_event.get('aimed_at_teachers', ''), #not present
                #'data_scientists': one_event.get('aimed_at_data_scientists', ''), # not present
                'description': one_event.get('description', ''),
                #'ical_id': one_event.get('ical_id', ''), # id? otherwise not used
                'room': one_event.get('room', ''),
                'track': one_event.get('track', ''),
                'day_date': one_day, # name of day?
                'start_time': one_event.get('time', ''), # start
                #'end_time': one_event.get('end_time', '') # start + duration?
            }
            return parsed_event

        parsed_schedule = {}
        ## here we parse json
        #self.raw_schedule["schedule"]["conference"]["days"]
        days = self.raw_schedule["schedule"]["conference"]["days"]
        days.sort(key=lambda d: d["index"])
        for day in days:
            for room in day["rooms"].values():
                for event in room:
                    temp = parse_one_event(event)
                    parsed_schedule[temp["id"]] = temp
            # day_data = self.raw_schedule[day]
            # We don't need to parse these, but leave the code in case we want it later
            # time_lookup = get_times(day_data['times'])
            # room_lookup = get_rooms(day_data['rooms'])
            # for time_number in range(len(day_data['matrix'])):
            #     event_list = day_data['matrix'][time_number]
            #     for event_index in range(len(event_list)):
            #         if interesting_event(event_list[event_index]):
            #             parsed_schedule[event_list[event_index]['id'].lower()] = \
            #                 parse_one_event(day, event_list[event_index])
        return parsed_schedule

    def get_upload_details(self, event_id):
        return self.parsed_schedule.get(event_id, None)

    def get_formatted_details(self, event_id):
        this_event = self.parsed_schedule.get(event_id, None)
        if not this_event:
            return None

        subtitle_string = ('.. ' + this_event['subtitle']) if this_event['subtitle'] else ''
        speaker_string = '.. ' + this_event['speaker']
        event_string = this_event['room'] + ' ' + this_event['day_date'] + ' ' + \
            this_event['start_time'] + '-' + this_event['end_time']

        track_string = ('Track: ' + this_event['track']) if this_event['track'] else ''

        suitable_for = [each for each in [
            'New programmers' if this_event['new_programmers'] else '',
            'Teachers' if this_event['teachers'] else '',
            'Data scientists' if this_event['data_scientists'] else ''
        ] if each]
        if any(suitable_for):
            suitable_for_string = 'Suitable for: ' + ', '.join(suitable_for)
        else:
            suitable_for_string = ''

        # Might also need to truncate very long descriptions
        clean_description_string = all_text_cleaning(this_event['description'])

        # List comprehension suppresses fully blank lines, while allowing '  ' as a spacing line
        description_lines = [each for each in [
            this_event['title'],
            subtitle_string,
            speaker_string,
            '  ',
            event_string,
            track_string,
            suitable_for_string,
            '  ',
            clean_description_string
        ] if each]
        description_string = squash_empty_lines('\n'.join(description_lines))

        more_keywords = [each for each in [
            'education' if this_event['track'].lower().find('education') else '',
            'pydata' if this_event['track'].lower().find('pydata') else '',
            'teaching' if this_event['teachers'] else '',
            'data science' if this_event['data_scientists'] else '',
            'beginner' if this_event['new_programmers'] else ''
        ] if each]
        keyword_string = ','.join(COMMON_KEYWORDS + more_keywords)

        metadata = dict(id=this_event['id'].lower(), title=this_event['title'], description=description_string,
                        keywords=keyword_string)
        return metadata


class ReadyVideos:
    def __init__(self, schedule_data, config_data):
        self.sd = schedule_data
        self.cd = config_data
        self.ready_dir = os.path.join(self.cd['v_root'], self.cd['v_ready'])
        self.no_launch_dir = os.path.join(self.cd['v_root'], self.cd['v_no_launch'])
        self.completed_dir = os.path.join(self.cd['v_root'], self.cd['v_completed'])
        self.failed_dir = os.path.join(self.cd['v_root'], self.cd['v_failed'])
        self.auth_dir = os.path.join(self.cd['v_root'], self.cd['v_auth'])
        self.v_mask = '*.' + self.cd['v_ext']
        self.v_ready_list = []
        self.ready_count = 0
        self.no_launch_count = 0
        self.completed_count = 0
        self.failed_count = 0

    def find_videos(self):
        print('Looking for video files in {}'.format(self.ready_dir))
        for a_file in os.listdir(self.ready_dir):
            if fnmatch.fnmatch(a_file, self.v_mask):
                self.v_ready_list.append(a_file)
        self.ready_count = len(self.v_ready_list)
        print('Found {} file(s) matching {}'.format(self.ready_count, self.v_mask))

    def write_all_youtube_metadata(self):
        for event_id in self.sd:
            metadata = self.sd.get_formatted_details(event_id)
            # Nice to write this to a file, but just for testing, so write to screen and copy paste
            for item in metadata:
                print(metadata[item])
            print('\n')
            print('-' * 80)

    def upload_all_videos(self):
        def get_id_from_name(file_name):
            # We want a name that is at least xxxx.ext long
            # More precisely, we should strip the extension and check for 4 characters

            # new file naming convention - split on underscores

            if len(file_name) < 8:
                return None

            underscore_sections = file_name.split("_")
            # return file_name[:4].lower()
            return underscore_sections[1]

        def move_one_file(the_file, from_dir, to_dir):
            try:
                os.rename(os.path.join(from_dir, the_file), os.path.join(to_dir, the_file))
            except (IOError, OSError):
                print('Could not move {} from {} to {}'.format(the_file, from_dir, to_dir))

        def format_session_data(session):
            return session

        if len(self.v_ready_list):
            yt_service = uv.get_authenticated_service(self.auth_dir)
        else:
            yt_service = None
        while len(self.v_ready_list):
            # The intent of 'done_this' is to ensure atomicity, but we are not achieving this objective
            # with the code as it exists
            done_this = False
            v_file_name = self.v_ready_list[0]
            v_id = get_id_from_name(v_file_name)
            if not v_id:
                move_one_file(v_file_name, self.ready_dir, self.no_launch_dir)
                self.no_launch_count += 1
                done_this = True
            else:
                # v_session_data = self.sd.get_upload_details(v_id)
                v_session_data = self.sd.get_formatted_details(v_id)
                if not v_session_data:
                    move_one_file(v_file_name, self.ready_dir, self.no_launch_dir)
                    self.no_launch_count += 1
                    done_this = True
                else:
                    yt_session_data = format_session_data(v_session_data)
                    yt_session_data = YTSessionData(os.path.join(self.ready_dir, v_file_name), self.cd['v_category'],
                                                    self.cd['v_privacy'], yt_session_data)
                    yt_video_id = uv.upload_video(yt_service, yt_session_data)
                    if yt_video_id:
                        move_one_file(v_file_name, self.ready_dir, self.completed_dir)
                        self.completed_count += 1
                    else:
                        move_one_file(v_file_name, self.ready_dir, self.failed_dir)
                        self.failed_count += 1
                    done_this = True
            if done_this:
                self.v_ready_list.pop(0)


def print_usage():
    # Do we need anything here?
    # We will get messages or errors from get_config
    pass


def make_one_dir(dir_path):
    try:
        os.makedirs(dir_path, exist_ok=True)
    except (IOError, OSError):
        print('Could not create directory {}'.format(dir_path))
        return False
    return True


def make_all_dirs(all_dirs):
    # v_root must be an absolute path
    v_root = all_dirs.get('v_root', None)
    if not v_root:
        print('No video root directory specified')
        sys.exit(1)
    all_dirs_made = True
    try:
        if not os.path.isdir(v_root):
            if not make_one_dir(v_root):
                all_dirs_made = False
        # If we're still ok, make / confirm the other directories
        if all_dirs_made:
            for d in all_dirs:
                if d not in ['v_root', 'v_ext']:
                    if not make_one_dir(os.path.join(v_root, all_dirs[d])):
                        all_dirs_made = False
    except (IOError, OSError):
        print('Could not write to one or more directories')
        sys.exit(1)
    if not all_dirs_made:
        print('Could not create one or more directories')
        sys.exit(1)


def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--category', default='22',
                        help='Numeric video category. ' +
                             'See https://developers.google.com/youtube/v3/docs/videoCategories/list')
    parser.add_argument('--privacy', choices=VALID_PRIVACY_STATUSES,
                        default='private', help='Video privacy status.')
    parser.add_argument('--root', required=True,
                        help='Base file path (absolute directory) for video upload functions')
    args = parser.parse_args()
    c = {
        'v_root': args.root,
        'v_ready': READY_FOR_UPLOAD,
        'v_no_launch': COULD_NOT_START_UPLOAD,
        'v_completed': COMPLETED_UPLOAD,
        'v_failed': FAILED_UPLOAD,
        'v_auth': VIDEO_SERVICE_AUTH
    }
    make_all_dirs(c)
    c['v_ext'] = VIDEO_FILE_EXTENSION
    c['v_privacy'] = args.privacy
    c['v_category'] = args.category

    # TODO: Read config from ~/.pycon_capture/pycon_capture.yml
    # home_dir = os.path.expanduser('~')
    # if not os.path.isdir(home_dir):
    #     try:
    #         os.makedirs(home_dir, exist_ok=True)
    #     except IOError:
    #         print('Could not create configuration directory at {}'.format(home_dir))
    #         sys.exit(1)
    return c


if __name__ == '__main__':
    print_usage()
    config = get_config()
    schedule = ScheduleData()
    ready_videos = ReadyVideos(schedule, config)
    # ready_videos.write_all_youtube_metadata()
    ready_videos.find_videos()
    ready_videos.upload_all_videos()
