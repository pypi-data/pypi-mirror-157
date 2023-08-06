##########################################################################################################################################################################
# the import lib block
##########################################################################################################################################################################
import json
import os
import time
import threading

##########################################################################################################################################################################
# the Constant block
##########################################################################################################################################################################
from configparser import ConfigParser, NoSectionError, NoOptionError

HOUR_PER_DAY        = 24
MIN_PER_DAY         = 60 * 24
SECONDS_PER_DAY     = 60 * 60 * 24
MIN_PER_HOUR        = 60
SECONDS_PER_HOUR    = 60 * 60

#  for firebase
FB_CHECK_TIMEOUT = 600
FB_HAS_LOADED_FILE_PATH = '/bigquery/script/pythonCode/tmpDir/'


DATA_UNIT           = 1024

SEPARATOR_UNDERLINE = '_'
SEPARATOR_DASH      = '-'
SEPARATOR_DOT       = '.'
SEPARATOR_NONE      = ''

ADMIN_MAIL          = 'qvdingcheng@gamebeartech.com'
ADMIN_MAIL_LIST     = ['qvdingcheng@gamebeartech.com',
                       'zhangqing@gamebeartech.com',
                       'lvanbang@gamebeartech.com']
OPERATION_MAIL_LIST = ['liuyu@gamebeartech.com',
                       'qvdingcheng@gamebeartech.com',
                       'zhangqing@gamebeartech.com',
                       'lvanbang@gamebeartech.com',
                       'wangnannan@gamebeartech.com',
                       'wusiqian@gamebeartech.com',
                       'qiujin@gamebeartech.com']
PGAME_OP_LIST       = ['qvdingcheng@gamebeartech.com',
                       'zhangqing@gamebeartech.com',
                       'shuzuhang@gamebeartech.com',
                       'daijie@gamebeartech.com',
                       'xueshuang@gamebeartech.com',
                       'xiekai@gamebeartech.com']


CSV_TMP_DIR_PATH    = '/bigquery/script/pythonCode/tmpCsvDir/'

#  for market
MKT_CSV_TMP_DIR_PATH    = '/bigquery/script/pythonCode/tmpCsvDir/'
NOVA_MKT_METHOD_PATH    = '/bigquery/script/pythonCode/nova/market/'
MKT_RECORD_PATH         = '/bigquery/script/pythonCode/log/market_record.log'
STATUS_FILE_NAME        = 'statusFile'

CMD_INPUT_CNT           = 6
CMD_INPUT_SINGLE_CNT    = 7

PLATFORM_ANDROID    = 'ANDROID'
PLATFORM_IOS        = 'IOS'
PLATFORM_ALL        = 'ALL'

QUERY_TYPE_SINGLE       = 'single'
QUERY_TYPE_ALL          = 'all'

FLIST_OFFSET        = 1

THREAD_NAME_BASE_STR = 'THREAD_'
THREAD_LOCK          = threading.Lock()
THREAD_DRY_RUN_LIMIT = 25  # https://cloud.google.com/bigquery/quotas#queries        #max is 50


##########################################################################################################################################################################
# the function block
##########################################################################################################################################################################
# Integer judgment
def is_integer(a_string):
	try:
		int(a_string)
		return True
	except ValueError:
		return False


# The decimal judgments
def is_float(a_string):
	try:
		float(a_string)
		return True
	except ValueError:
		return False


# Positive integer judgment
def is_number(a_string):
	try:
		if int(a_string) > 0:
			return True
		else:
			return False
	except ValueError:
		return False


def is_email(a_string):
	if a_string.endswith("@gamebeartech.com"):
		return True
	else:
		return False


def lr_strip(a_string):
	return a_string.lstrip().rstrip()


# for market
def is_valid_platform(platform_str):
	if platform_str in (PLATFORM_ALL, PLATFORM_IOS, PLATFORM_ANDROID):
		return True
	return False


def is_valid_query_type(qr_type_str):
	if qr_type_str in (QUERY_TYPE_SINGLE, QUERY_TYPE_ALL):
		return True
	return False


def log_mkt_add(log_path, py_name, e_mail, params):
	time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	
	flog = open(log_path, 'a')
	log_str = ''
	log_str += 'Time[' + time_str + '] '
	log_str += 'pyName[' + py_name + '] '
	log_str += 'e-mail[' + e_mail + '] '
	log_str += 'params[' + params + ']\n'
	flog.write(log_str)
	flog.close()


# prepare for the final list
def prepare_final_list(f_list, d_cnt, qr_type):
	m_cnt = len(f_list)
	i     = 0

	if qr_type == QUERY_TYPE_ALL:
		while i < m_cnt:
			j = 0

			while j < d_cnt:
				f_list[i].append(0)
				j += 1

			i += 1
	elif qr_type == QUERY_TYPE_SINGLE:
		while i < m_cnt:
			f_list[i].append(0)

			i += 1


def update_final_list(method, f_list, item_list, dx, qr_type):
	f_list_cnt = len(f_list)
	
	if NOVA_MKT_METHOD_PATH in method:
		split_list = method.split('/')
		method = split_list[len(split_list) - 1]

	method_1 = [
		'mediaRetention.py',
		'mediaPurchaseRate.py',
	]

	method_2 = [
		'mediaCountryRetention.py',
		'mediaCountryLtv.py',
		'mediaCountryArppu.py',
		'mediaKeywordsLtv.py',
		'mediaKeywordsArppu.py',
		'mediaCountryLevel5Dau.py',
		'mediaCountryLevel6Dau.py',
		'mediaCountryPurchaseRate.py',
	]

	dx_offset = 0
	if method in method_1:
		if qr_type == QUERY_TYPE_ALL:
			dx_offset = dx + FLIST_OFFSET
		elif qr_type == QUERY_TYPE_SINGLE:
			dx_offset = 1 + FLIST_OFFSET

		i = 0
		while i < f_list_cnt:
			if item_list[0] == f_list[i][0]:
				f_list[i][dx_offset] += item_list[1]
				break
		
			i += 1
	elif method in method_2:
		if qr_type == QUERY_TYPE_ALL:
			dx_offset = dx + 2 * FLIST_OFFSET
		elif qr_type == QUERY_TYPE_SINGLE:
			dx_offset = 2 + FLIST_OFFSET

		i = 0
		while i < f_list_cnt:
			if item_list[0] == f_list[i][0] and item_list[1] == f_list[i][1]:
				f_list[i][dx_offset] += item_list[2]
				break

			i += 1


def completion_country_words(f_list):
	country_dict_af = {
		"AF": "Afghanistan                     ", "AO": "Angola                         ", "AD": "Andorra                        ", "AX": "Aland Islands                  ", "AL": "Albania                        ",
		"DZ": "Algeria                         ", "AS": "American Samoa                 ", "AI": "Anguilla                       ", "AQ": "Antarctica                     ", "AG": "Antigua And Barbuda            ", "AR": "Argentina                      ",
		"AM": "Armenia                         ", "AW": "Aruba                          ", "AU": "Australia                      ", "AT": "Austria                        ", "AZ": "Azerbaijan                     ", "BS": "Bahamas                        ",
		"BH": "Bahrain                         ", "BD": "Bangladesh                     ", "BB": "Barbados                       ", "BY": "Belarus                        ", "BE": "Belgium                        ", "BZ": "Belize                         ",
		"BJ": "Benin                           ", "BM": "Bermuda                        ", "BT": "Bhutan                         ", "BO": "Bolivia                        ", "BA": "Bosnia And Herzegovina         ", "BW": "Botswana                       ",
		"BV": "Bouvet Island                   ", "BR": "Brazil                         ", "IO": "British Indian Ocean Territory ", "BN": "Brunei Darussalam              ", "BG": "Bulgaria                       ", "BF": "Burkina Faso                   ",
		"BI": "Burundi                         ", "KH": "Cambodia                       ", "CM": "Cameroon                       ", "CA": "Canada                         ", "CV": "Cape Verde                     ", "KY": "Cayman Islands                 ",
		"CF": "Central African Republic        ", "TD": "Chad                           ", "CL": "Chile                          ", "CN": "China                          ", "CX": "Christmas Island               ", "CC": "Cocos Islands                  ",
		"CO": "Colombia                        ", "KM": "Comoros                        ", "CG": "Congo                          ", "CD": "Congo Democratic Republic      ", "CK": "Cook Islands                   ", "CR": "Costa Rica                     ",
		"CI": "Cote D'Ivoire                   ", "HR": "Croatia                        ", "CU": "Cuba                           ", "CY": "Cyprus                         ", "CZ": "Czech Republic                 ", "DK": "Denmark                        ",
		"DJ": "Djibouti                        ", "DM": "Dominica                       ", "DO": "Dominican Republic             ", "EC": "Ecuador                        ", "EG": "Egypt                          ", "SV": "El Salvador                    ",
		"GQ": "Equatorial Guinea               ", "ER": "Eritrea                        ", "EE": "Estonia                        ", "ET": "Ethiopia                       ", "FK": "Falkland Islands               ", "FO": "Faroe Islands                  ",
		"FJ": "Fiji                            ", "FI": "Finland                        ", "FR": "France                         ", "GF": "French Guiana                  ", "PF": "French Polynesia               ", "TF": "French Southern Territories    ",
		"GA": "Gabon                           ", "GB": "Great Britain                  ", "GM": "Gambia                         ", "GE": "Georgia                        ", "DE": "Germany                        ", "GH": "Ghana                          ",
		"GI": "Gibraltar                       ", "GR": "Greece                         ", "GL": "Greenland                      ", "GD": "Grenada                        ", "GP": "Guadeloupe                     ", "GU": "Guam                           ",
		"GT": "Guatemala                       ", "GG": "Guernsey                       ", "GN": "Guinea                         ", "GW": "Guinea-Bissau                  ", "GY": "Guyana                         ", "HT": "Haiti                          ",
		"HM": "Heard Island & Mcdonald Islands ", "VA": "Holy See                       ", "HN": "Honduras                       ", "HK": "Hong Kong                      ", "HU": "Hungary                        ", "IS": "Iceland                        ",
		"IN": "India                           ", "ID": "Indonesia                      ", "IR": "Iran Islamic Republic Of       ", "IQ": "Iraq                           ", "IE": "Ireland                        ", "IM": "Isle Of Man                    ",
		"IL": "Israel                          ", "IT": "Italy                          ", "JM": "Jamaica                        ", "JP": "Japan                          ", "JE": "Jersey                         ", "JO": "Jordan                         ",
		"KZ": "Kazakhstan                      ", "KE": "Kenya                          ", "KI": "Kiribati                       ", "KR": "Korea                          ", "KW": "Kuwait                         ", "KG": "Kyrgyzstan                     ",
		"LA": "Lao People's Democratic Republic", "LV": "Latvia                         ", "LB": "Lebanon                        ", "LS": "Lesotho                        ", "LR": "Liberia                        ", "LY": "Libyan Arab Jamahiriya         ",
		"LI": "Liechtenstein                   ", "LT": "Lithuania                      ", "LU": "Luxembourg                     ", "MO": "Macao                          ", "MK": "Macedonia                      ", "MG": "Madagascar                     ",
		"MW": "Malawi                          ", "MY": "Malaysia                       ", "MV": "Maldives                       ", "ML": "Mali                           ", "MT": "Malta                          ", "MH": "Marshall Islands               ",
		"MQ": "Martinique                      ", "MR": "Mauritania                     ", "MU": "Mauritius                      ", "YT": "Mayotte                        ", "MX": "Mexico                         ", "FM": "Micronesia Federated States Of ",
		"MD": "Moldova                         ", "MC": "Monaco                         ", "MN": "Mongolia                       ", "ME": "Montenegro                     ", "MS": "Montserrat                     ", "MA": "Morocco                        ",
		"MZ": "Mozambique                      ", "MM": "Myanmar                        ", "NA": "Namibia                        ", "NR": "Nauru                          ", "NP": "Nepal                          ", "NL": "Netherlands                    ",
		"AN": "Netherlands Antilles            ", "NC": "New Caledonia                  ", "NZ": "New Zealand                    ", "NI": "Nicaragua                      ", "NE": "Niger                          ", "NG": "Nigeria                        ",
		"NU": "Niue                            ", "NF": "Norfolk Island                 ", "MP": "Northern Mariana Islands       ", "NO": "Norway                         ", "OM": "Oman                           ", "PK": "Pakistan                       ",
		"PW": "Palau                           ", "PS": "Palestinian Territory          ", "PA": "Panama                         ", "PG": "Papua New Guinea               ", "PY": "Paraguay                       ", "PE": "Peru                           ",
		"PH": "Philippines                     ", "PN": "Pitcairn                       ", "PL": "Poland                         ", "PT": "Portugal                       ", "PR": "Puerto Rico                    ", "QA": "Qatar                          ",
		"RE": "Reunion                         ", "RO": "Romania                        ", "RU": "Russian Federation             ", "RW": "Rwanda                         ", "BL": "Saint Barthelemy               ", "SH": "Saint Helena                   ",
		"KN": "Saint Kitts And Nevis           ", "LC": "Saint Lucia                    ", "MF": "Saint Martin                   ", "PM": "Saint Pierre And Miquelon      ", "VC": "Saint Vincent And Grenadines   ", "WS": "Samoa                          ",
		"SM": "San Marino                      ", "ST": "Sao Tome And Principe          ", "SA": "Saudi Arabia                   ", "SN": "Senegal                        ", "RS": "Serbia                         ", "SC": "Seychelles                     ",
		"SL": "Sierra Leone                    ", "SG": "Singapore                      ", "SK": "Slovakia                       ", "SI": "Slovenia                       ", "SB": "Solomon Islands                ", "SO": "Somalia                        ",
		"ZA": "South Africa                    ", "GS": "South Georgia And Sandwich Isl.", "ES": "Spain                          ", "LK": "Sri Lanka                      ", "SD": "Sudan                          ", "SR": "Suriname                       ",
		"SJ": "Svalbard And Jan Mayen          ", "SZ": "Swaziland                      ", "SE": "Sweden                         ", "CH": "Switzerland                    ", "SY": "Syrian Arab Republic           ", "TW": "Taiwan                         ",
		"TJ": "Tajikistan                      ", "TZ": "Tanzania                       ", "TH": "Thailand                       ", "TL": "Timor-Leste                    ", "TG": "Togo                           ", "TK": "Tokelau                        ",
		"TO": "Tonga                           ", "TT": "Trinidad And Tobago            ", "TN": "Tunisia                        ", "TR": "Turkey                         ", "TM": "Turkmenistan                   ", "TC": "Turks And Caicos Islands       ",
		"TV": "Tuvalu                          ", "UG": "Uganda                         ", "UA": "Ukraine                        ", "AE": "United Arab Emirates           ", "UK": "United Kingdom                 ", "US": "United States                  ",
		"UM": "United States Outlying Islands  ", "UY": "Uruguay                        ", "UZ": "Uzbekistan                     ", "VU": "Vanuatu                        ", "VE": "Venezuela                      ", "VN": "Viet Nam                       ",
		"VG": "Virgin Islands British          ", "VI": "Virgin Islands U.S.            ", "WF": "Wallis And Futuna              ", "EH": "Western Sahara                 ", "YE": "Yemen                          ", "ZM": "Zambia                         ",
		"ZW": "Zimbabwe                        ", "CW": "Curacao                        "}

	for eachList in f_list:
		if eachList[1] in country_dict_af:
			eachList[1] = country_dict_af[eachList[1]]


def convert_country_str(country):
	if country is None:
		new_country_str = ''
	else:
		try:
			country_byte = country.encode('utf-8')
		except AttributeError:
			new_country_str = str(country)
		else:
			if country_byte   == b'R\xc3\xa9union':
				new_country_str = 'Reunion'
			elif country_byte == b'Cura\xc3\xa7ao':
				new_country_str = 'Curacao'
			elif country_byte == b'\xc3\x85land Islands':
				new_country_str = 'Aland Islands'
			elif country_byte == b'C\xc3\xb4te d\xe2\x80\x99Ivoire':
				new_country_str = "Cote D'Ivoire"
			elif country_byte == b'St. Barth\xc3\xa9lemy':
				new_country_str = "Saint Barthelemy"
			elif country_byte == b'S\xc3\xa3o Tom\xc3\xa9 & Pr\xc3\xadncipe':
				new_country_str = 'Sao Tome And Principe'

			elif country_byte == b'Antigua & Barbuda':
				new_country_str = 'Antigua And Barbuda'
			elif country_byte == b'Bosnia & Herzegovina':
				new_country_str = 'Bosnia And Herzegovina'
			elif country_byte == b'Brunei':
				new_country_str = 'Brunei Darussalam'
			elif country_byte == b'Congo - Brazzaville':
				new_country_str = 'Congo'
			elif country_byte == b'Congo - Kinshasa':
				new_country_str = 'Congo Democratic Republic'
			elif country_byte == b'Czechia':
				new_country_str = 'Czech Republic'
			elif country_byte == b'Iran':
				new_country_str = 'Iran Islamic Republic Of'
			elif country_byte == b'South Korea':
				new_country_str = 'Korea'
			elif country_byte == b'Laos':
				new_country_str = "Lao People's Democratic Republic"
			elif country_byte == b'Libya':
				new_country_str = 'Libyan Arab Jamahiriya'
			elif country_byte == b'Macau':
				new_country_str = 'Macao'
			elif country_byte == b'Macedonia (FYROM)':
				new_country_str = 'Macedonia'
			elif country_byte == b'Micronesia':
				new_country_str = 'Micronesia Federated States Of'
			elif country_byte == b'Myanmar (Burma)':
				new_country_str = 'Myanmar'
			elif country_byte == b'Palestine':
				new_country_str = 'Palestinian Territory'
			elif country_byte == b'Russia':
				new_country_str = 'Russian Federation'
			elif country_byte == b'St. Lucia':
				new_country_str = 'Saint Lucia'
			elif country_byte == b'Sint Maarten':
				new_country_str = 'Saint Martin'
			elif country_byte == b'St. Pierre & Miquelon':
				new_country_str = 'Saint Pierre And Miquelon'
			elif country_byte == b'St. Vincent & Grenadines':
				new_country_str = 'Saint Vincent And Grenadines'
			elif country_byte == b'Syria':
				new_country_str = 'Syrian Arab Republic'
			elif country_byte == b'Trinidad & Tobago':
				new_country_str = 'Trinidad And Tobago'
			elif country_byte == b'Turks & Caicos Islands':
				new_country_str = 'Turks And Caicos Islands'
			elif country_byte == b'Vietnam':
				new_country_str = 'Viet Nam'
			elif country_byte == b'British Virgin Islands':
				new_country_str = 'Virgin Islands British'
			elif country_byte == b'U.S. Virgin Islands':
				new_country_str = 'Virgin Islands U.S.'
			else:
				new_country_str = str(country)

	return new_country_str


class GbConfig:
	def __init__(self):
		base_dir = os.path.dirname(os.path.abspath(__file__))
		config = ConfigParser()
		if os.path.exists(os.path.join(base_dir, 'Config.local.cfg')):
			config.read(os.path.join(base_dir, 'Config.local.cfg'), encoding='utf-8')
		else:
			config.read(os.path.join(base_dir, 'Config.cfg'), encoding='utf-8')
		self.config = config

	def get(self, section, option):
		try:
			return self.config.get(section, option)
		except NoSectionError:
			raise Exception("can't find project_name: {}".format(section))
		except NoOptionError:
			raise Exception("can't find option name, please check config.cfg")
