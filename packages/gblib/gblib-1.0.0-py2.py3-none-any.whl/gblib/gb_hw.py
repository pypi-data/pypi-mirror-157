
import os
import psutil


# Return the number of logical CPUs in the system
def get_cpu_count_logical():
	return psutil.cpu_count(logical=True)


# return the number of physical cores
def get_cpu_count_physical():
	return psutil.cpu_count(logical=False)


def get_cpu_load_average():
	poepn_ret = os.popen(f'w').readlines()
	split_ret = poepn_ret[0].replace('\n', '').split(',')
	split_ret[-3] = split_ret[-3].split(':')[-1]
	avg_1_min = split_ret[-3].replace(' ', '')
	avg_5_min = split_ret[-2].replace(' ', '')
	avg_15_min = split_ret[-1].replace(' ', '')
	return float(avg_1_min), float(avg_5_min), float(avg_15_min)


# Total memory usage
def get_total_memory():
	mem = psutil.virtual_memory()
	return mem.total


# Used memory usage
def get_used_memory():
	mem = psutil.virtual_memory()
	return mem.used


# the percentage memory usage
def get_percentage_memory():
	mem = psutil.virtual_memory()
	return mem.percent


# Return mounted partitions as a list of (device, mountpoint, fstype, opts) namedtuple
def get_all_disk():
	return psutil.disk_partitions()


# Total disk total size(Bytes)
def get_total_disk(path):
	return psutil.disk_usage(path)[0]


# Used disk usage size(Bytes)
def get_used_disk(path):
	return psutil.disk_usage(path)[1]
