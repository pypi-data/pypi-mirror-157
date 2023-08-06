

##########################################################################################################################################################################
# the import lib block
##########################################################################################################################################################################
import os
import codecs

##########################################################################################################################################################################
# the Constant block
##########################################################################################################################################################################
SIZE_UNIT_BYTE  = 'Byte'
SIZE_UNIT_KB    = 'KB'
SIZE_UNIT_MB    = 'MB'
SIZE_UNIT_GB    = 'GB'
SIZE_UNIT_TB    = 'TB'

# file extention
EXT_LOG     = '.log'
EXT_JSON    = '.json'
EXT_TXT     = '.txt'


##########################################################################################################################################################################
# the function block
##########################################################################################################################################################################
def file_exist(f_name):
	return os.path.exists(f_name)


def file_create(f_name):
	if not file_exist('./' + f_name):
		with open(f_name, 'w'):
			pass
	else:
		raise FileExistsError('The file already exists')


def file_delete(f_name):
	try:
		return os.remove(f_name)
	except FileNotFoundError:
		raise FileNotFoundError


def file_write(f_name, string, *mode):
	if mode == 'b':
		with open(f_name, 'wb') as fw:
			fw.write(string)
	else:
		with open(f_name, 'w') as fw:
			fw.write(string)


def file_read(f_name, *mode):
	if mode == 'b':
		with open(f_name, 'rb') as fr:
			return fr.read()
	else:
		with open(f_name, 'r') as fr:
			return fr.read()


def file_get_line_cnt(f_name):
	f = open(f_name)
	return len(f.readlines())


def get_file_size(f_name, unit = SIZE_UNIT_BYTE):
	fsize = os.path.getsize(f_name)
	
	if unit == SIZE_UNIT_BYTE:
		return fsize
	elif unit == SIZE_UNIT_KB:
		fsize = fsize / float(1024)
	elif unit == SIZE_UNIT_MB:
		fsize = fsize / float(1024 * 1024)
	elif unit == SIZE_UNIT_GB:
		fsize = fsize / float(1024 * 1024 * 1024)
	elif unit == SIZE_UNIT_TB:
		fsize = fsize / float(1024 * 1024 * 1024 * 1024)

	return round(fsize, 2)


def get_file_list(dir_path, type = 'all', recursion = None):
	f_list = list()
	if recursion and recursion == 'r':  # recursion exists and value is 'r'
		for root, dirs, files in os.walk(dir_path):
			for file in files:
				if type and type != 'all':
					if file.endswith(type):
						f_list.append(os.path.join(root, file))
				else:
					f_list.append(os.path.join(root, file))
		return f_list
	else:  # not recursion
		for root, dirs, files in os.walk(dir_path):
			for file in files:
				if type and type != 'all':
					if file.endswith(type):
						f_list.append(os.path.join(root, file))
				else:
					f_list.append(os.path.join(root, file))
			return f_list


def convert(file_name, file, in_code="latin1", out_code="UTF-8"):
	try:
		with codecs.open(file_name, 'r', in_code) as f_in:
			new_content = f_in.read()
			f_out = codecs.open(os.path.join(file), 'w', out_code)
			f_out.write(new_content)
			f_out.close()
			f_in.close()
	except IOError as err:
		print("I/O error: {0}".format(err))


def gb_path_join(path, *args):
	return os.path.normpath(os.path.join(path, *args))
