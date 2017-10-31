import datetime as dt
import re

TIME_PATTERN = re.compile("([01]?[0-9]|2[0-3]):([0-5][0-9])")
MIDNIGHT = dt.datetime.min


def time_now():
	return dt.datetime.now()


def time_midnight():
	return MIDNIGHT


def string_to_time(time_string, add_minutes=0):
    match = TIME_PATTERN.match(time_string)
    if match:
        return dt.datetime.min + dt.timedelta(hours=int(match[1]), minutes=int(match[2])) + dt.timedelta(minutes=add_minutes)
    else:
        return MIDNIGHT


def time_to_string(t):
    return t.strftime('%H:%M')


def prior_half_hour(this_time):
	return this_time - dt.timedelta(minutes=30)


def half_hour_start(this_time):
	minutes = int(this_time.strftime('%M'))
	# print('minutes={}'.format(minutes))
	if minutes in [0, 30]:
		return this_time
	elif 1 <= minutes <= 29:
		return this_time - dt.timedelta(minutes=minutes)
	elif 31 <= minutes <= 59:
		return this_time - dt.timedelta(minutes=minutes-30)


def half_hour_end(this_time):
	# This is only 29 minutes for ease of database querying
	return this_time + dt.timedelta(minutes=29)


class Timeslot():
	def __init__(self, this, period='current'):
		if isinstance(this, dt.datetime):
			self.this = this
		elif isinstance(this, str):
			self.this = string_to_time(this)
		else:
			raise ValueError('Timeslot must be created with datetime or string')
		# print('period={}'.format(period))
		if period == 'prior':
			self.this = prior_half_hour(self.this)

		self.start = half_hour_start(self.this)
		self.finish = half_hour_end(self.start)

		# print('start={}'.format(self.start))
		# print('finish={}'.format(self.finish))

	def __str__(self):
		return time_to_string(self.start)


if __name__ == '__main__':
	n = dt.datetime.now()
	print('now={}'.format(n))
	t = Timeslot(n, 'current')
	print('timeslot={}'.format(t))
	t = Timeslot(n, 'prior')
	print('timeslot={}'.format(t))
	t = Timeslot('11:45', 'current')
	print('timeslot={}'.format(t))
	t = Timeslot('11:45', 'prior')
	print('timeslot={}'.format(t))
