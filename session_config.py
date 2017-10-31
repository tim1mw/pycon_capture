import yaml
import argparse
import timeslot

CONFIG_FILENAME = 'session_config.yml'

SESSION_METADATA_PATH = '/usr/local/src/pycon/2017/pyconuk_website/'
SESSION_METADATA_DB = 'db.sqlite3'
VIDEO_TITLE_PREFIX = 'PYCON UK'
CONFERENCE_YEAR = 2017
TEST_DAY = ''
TEST_TIME = ''

EMPTY_CONFIG = {
    'session_metadata_path': '',
    'session_metadata_db': '',
    'video_title_prefix': '',
    'conference_year': 0,
    'test_day': '',
    'test_time': ''
    }

BASE_CONFIG = {
    'session_metadata_path': SESSION_METADATA_PATH,
    'session_metadata_db': SESSION_METADATA_DB,
    'video_title_prefix': VIDEO_TITLE_PREFIX,
    'conference_year': CONFERENCE_YEAR,
    'test_day': TEST_DAY,
    'test_time': TEST_TIME
    }


def get_arguments(session_config):
    args = parse_args()
    if not args.now and not args.prior and args.time is None:
        args.now = True
    if session_config['test_day']:
        print('Using test day ="{}"'.format(session_config['test_day']))
        args.day = session_config['test_day']
    if session_config['test_time']:
        print('Using test time ="{}"'.format(session_config['test_time']))
        args.time = session_config['test_time']
        n = string_to_time(session_config['test_time'])
    else:
        n = dt.datetime.now()
    if args.now:
        args.time = str(Timeslot(n, 'current'))
    elif args.prior:
        args.time = str(Timeslot(n, 'prior'))
    else:
        args.time = str(Timeslot(args.time))
    return args


class SessionConfig(argparse.Namespace):
    def __init__(self, initialise=False):
        if initialise:
            self.write_config_file()
        self.read_arguments()
        self.read_config_file()
        self.add_config_to_namespace()
        self.normalise_config()

    def read_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--day", type=int, help="Select day - example 27 - omit for all")
        parser.add_argument("-r", "--room", type=str, help="Select partial room name - example 'ferrier' - omit for all")

        group1 = parser.add_mutually_exclusive_group()
        group1.add_argument("-t", "--time", type=str, help="Select time - example 14:30 - omit for all")
        group1.add_argument("-n", "--now", action="store_true", help="Select sessions on now")
        group1.add_argument("-p", "--prior", action="store_true", help="Select prior sessions")
        group2 = parser.add_mutually_exclusive_group()
        group2.add_argument("-l", "--long", action="store_true", help="Print long output (all fields, down the page")
        group2.add_argument("-b", "--bare", action="store_true", help="Print long and bare output (no field names)")
        # Add result items from argument parsing to our own dict, rather than create a separate object
        parser.parse_args(namespace=self)

    def write_config_file(self):
        config = BASE_CONFIG
        with open(CONFIG_FILENAME, 'w') as config_file:
            yaml.dump(config, config_file, default_flow_style=False)

    def read_config_file(self):
        self.config = EMPTY_CONFIG
        try:
            with open(CONFIG_FILENAME, 'r') as config_file:
                try:
                    self.config = yaml.safe_load(config_file)
                except yaml.YAMLError as e:
                    print("Error parsing yaml config file '{}'\n".format(CONFIG_FILENAME))
                    raise
        except IOError as e:
            print("Could not access yaml config file '{}'\n".format(CONFIG_FILENAME))
            raise

    def add_config_to_namespace(self):
        # Add all config items to our own dict
        for k,v in self.config.items():
            self.__dict__[k] = v

    def normalise_config(self):
        if not self.now and not self.prior and self.time is None:
            self.time = ''
        if self.config['test_day']:
            print('Using test day ="{}"'.format(self.config['test_day']))
            self.day = self.config['test_day']
        if self.config['test_time']:
            print('Using test time ="{}"'.format(self.config['test_time']))
            self.time = self.config['test_time']
            time = timeslot.string_to_time(self.config['test_time'])
        else:
            time = timeslot.time_now()
        if self.now:
            self.time = str(timeslot.Timeslot(time, 'current'))
        elif self.prior:
            self.time = str(timeslot.Timeslot(time, 'prior'))
        elif not self.time:
            pass
        else:
            self.time = str(timeslot.Timeslot(self.time))
        if not self.day:
            self.day = ''
        if not self.room:
            self.room = ''


if __name__ == '__main__':
    sc = SessionConfig(True)
    print(sc)
