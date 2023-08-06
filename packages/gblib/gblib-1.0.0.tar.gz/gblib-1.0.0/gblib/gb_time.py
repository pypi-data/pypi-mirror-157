##########################################################################################################################################################################
# the import lib block
##########################################################################################################################################################################
import time
import datetime
import pytz
import calendar
from gblib.gb_common import *

##########################################################################################################################################################################
# the Constant block
##########################################################################################################################################################################


##########################################################################################################################################################################
# the function block
##########################################################################################################################################################################
# The current time accurate to seconds
def get_cur_time_sec():
	return int(time.time())


# The current time accurate to millisecond
def get_cur_time_milli():
	return round(time.time(), 3)


# The current time accurate to microseconds
def get_cur_time_micro():
	return round(time.time(), 6)


# The current datetime accurate to microseconds
def get_cur_datetime():
	return datetime.datetime.utcnow()


def get_today_string(separator=SEPARATOR_DASH):
	today = datetime.datetime.now()

	if separator == SEPARATOR_DOT:
		return today.strftime('%Y.%m.%d')
	elif separator == SEPARATOR_UNDERLINE:
		return today.strftime('%Y_%m_%d')
	elif separator == SEPARATOR_NONE:
		return today.strftime('%Y%m%d')

	return today.strftime("%Y-%m-%d")


def get_yesterday_string(separator = SEPARATOR_DASH):
	yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
	fmt = ''
	if separator == SEPARATOR_DASH:
		fmt = "%Y-%m-%d"
	elif separator == SEPARATOR_UNDERLINE:
		fmt = "%Y_%m_%d"
	elif separator == SEPARATOR_NONE:
		fmt = "%Y%m%d"
	return yesterday.strftime(fmt)


def get_date_str_offset(day_str, offset, separator=SEPARATOR_DASH):
	base_time = time.mktime(time.strptime(day_str, '%Y-%m-%d'))
	offset_time = base_time + offset * SECONDS_PER_DAY

	x = time.localtime(offset_time)

	if separator == SEPARATOR_DOT:
		return time.strftime('%Y.%m.%d', x)
	elif separator == SEPARATOR_UNDERLINE:
		return time.strftime('%Y_%m_%d', x)
	elif separator == SEPARATOR_NONE:
		return time.strftime('%Y%m%d', x)

	return time.strftime('%Y-%m-%d', x)


def convert_date_str_format(src_date, src_fmt = '%Y-%m-%d', dest_fmt = '%Y%m%d'):
	try:
		s_time = time.mktime(time.strptime(src_date, src_fmt))
		tmp_time = time.localtime(s_time)
		dest_date = time.strftime(dest_fmt, tmp_time)
	except ValueError:
		print('parameter error!')
		return None

	return dest_date


def convert_ts_to_datetime(ts, fmt = '%Y-%m-%d %H:%M:%S', tz = 'Asia/Shanghai'):
	"""
	convert ts second/millisecond/microsecond to datetime/date format by standard timezone
	:param ts: int seconds or float microseconds
	:param fmt: standard fmt
	:param tz: standard timezone
	:return: return the converted result
	"""
	return datetime.datetime.fromtimestamp(ts, pytz.timezone(tz)).strftime(fmt)


def date_diff(start_d, end_d):
	"""
	date only support SEPRATOR_NONE format
	:param start_d:
	:param end_d:
	:return:
	"""
	dt_s = datetime.datetime(int(start_d[:4]), int(start_d[4:6]), int(start_d[6:]))
	dt_e = datetime.datetime(int(end_d[:4]), int(end_d[4:6]), int(end_d[6:]))
	return (dt_e - dt_s).days


'''
# Migration time
def migration_time(day):
	nowTime = time.time()
	return datetime.fromtimestamp(nowTime + 24 * 3600 * day)
'''


# Sleep for number seconds
def sleep_second(second):
	time.sleep(second)


# Sleep for number millisecond
def sleep_millisecond(millisecond):
	time.sleep(millisecond / 1000)


# check is a valid time format eg "2018-11-30"
def is_valid_date(date_str):
	try:
		time.strptime(date_str, "%Y-%m-%d")
		return True
	except ValueError:
		return False


# check is a valid time format eg "10:25:59"
def is_valid_time(time_str):
	try:
		time.strptime(time_str, '%H:%M:%S')
		return True
	except ValueError:
		return False


# check is a valid date and time format eg "2018-11-30 10:25:59"
def is_valid_datetime(datetime_str):
	try:
		time.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
		return True
	except ValueError:
		return False


def compare_time(start_t, end_t, if_end_date_eq_yesterday = False):
	"""
	for market
	Check the time range if valid
	start_time must less than or equal to end_time
	:param start_t:
	:param end_t:
	:param if_end_date_eq_yesterday:
	:return:
	"""
	s_time = time.mktime(time.strptime(start_t, '%Y-%m-%d'))  # get the seconds for specify date
	e_time = time.mktime(time.strptime(end_t, '%Y-%m-%d'))

	today_str = time.strftime("%Y-%m-%d", time.localtime())
	now_date = time.mktime(time.strptime(today_str, '%Y-%m-%d'))

	if int(s_time) > int(e_time):
		return False

	if if_end_date_eq_yesterday and int(e_time) + SECONDS_PER_DAY <= int(now_date):
		return True
	elif not if_end_date_eq_yesterday and int(e_time) + SECONDS_PER_DAY < int(now_date):
		return True

	return False


# cal the max Dx
def cal_Max_Dx(start_t, end_t, num):
	e_time = time.mktime(time.strptime(end_t, '%Y-%m-%d'))
	today_str = time.strftime("%Y-%m-%d", time.localtime())
	now_date = time.mktime(time.strptime(today_str, '%Y-%m-%d'))

	return min(int((now_date - e_time) / SECONDS_PER_DAY) - 1, int(num))


def get_days_by_year_month(year, month):
	"""
	get days by inputing year, month
	:param year:
	:param month:
	:return:
	"""
	return calendar.monthrange(year, month)[1]
