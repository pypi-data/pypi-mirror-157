# -*- coding: utf-8 -*-
# @Author  : rhc
# @Time    : 2020/8/5 18:37
import datetime
import sys

sys.path.append('/bigquery/script/pythonCode')
from gblib.gb_common import is_number, is_valid_platform, is_valid_query_type, is_email, PLATFORM_ALL, \
    NOVA_MKT_METHOD_PATH, log_mkt_add, MKT_RECORD_PATH, QUERY_TYPE_ALL, QUERY_TYPE_SINGLE
from gblib.gb_time import is_valid_date, cal_Max_Dx
from gblib.gb_google import bq_preparation

# 最小的起始时间
MIN_DATE = datetime.datetime.strptime('2020-05-01', '%Y-%m-%d')

# 参数个数
ARGUMENTS_COUNT = [7, 8]

# 查询字段字典
FIELD_DICTIONARIES = {
    'country': ['Country_Code'],
    'keywords': ['Keywords'],
    'siteid': ['Site_ID'],
    'ad_country': ['Ad', 'Country_Code']
}

# 提示信息
HELP_STR = '''The right CMD is: ***.py country/keywords/siteid/ad_country start_time end_time days android/ios/all single/all xxx@gamebeartech.com
	eg: python3 ***.py ad_country(not required) 2020-06-01 2020-06-30 5 all all qvdingcheng@gamebeartech.com
	ps:1.start_time must be less than or equal to end_time and must be at least 2020-05-01
	   2.end_time + one day must less than today'''


def check_arguments_add_log(arguments: list, filtered=False):
    """检查参数并记录日志"""
    print(arguments)
    # check arguments length
    if len(arguments) not in ARGUMENTS_COUNT:
        print('Parameter numbers Error!')
        return False

    # 截取参数
    py_name = arguments[0]
    start_date = arguments[-6]
    end_date = arguments[-5]
    days = arguments[-4]
    platform = arguments[-3].upper()
    query_type = arguments[-2].lower()
    email = arguments[-1].lower()
    paramsStr = 'start:' + start_date + ' end:' + end_date + ' days:' + days + ' platform:' + platform + ' queryType:' + query_type

    # check date
    if not is_valid_date(start_date) or not is_valid_date(end_date):
        print('date format error!')
        return False

    date_start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    date_end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    if date_start > date_end or date_start < MIN_DATE:
        print('start_time must be less than or equal to end_time and must be at least 2020-05-01')
        return False

    # check field
    if not filtered:
        field_name = arguments[1]
        paramsStr = 'field：' + field_name + paramsStr
        if field_name not in FIELD_DICTIONARIES:
            print('field_name error')
            return False

    # check days
    if not is_number(days):
        print('days error!')
        return False

    # check platform
    if not is_valid_platform(platform):
        print('platform error!')
        return False

    # check query_type
    if not is_valid_query_type(query_type):
        print('query type error!')
        return False

    # check email
    if not is_email(email):
        print('e-mail addr error!')
        return False

    # 记录日志
    if NOVA_MKT_METHOD_PATH in py_name:
        splitList = py_name.split('/')
        py_name = splitList[len(splitList) - 1]
    log_mkt_add(MKT_RECORD_PATH, py_name, email, paramsStr)

    return True


def get_media_install(arguments: list):
    """根据arguments计算不同维度的media安装数"""
    install_sql = """
SELECT
  "Organic" AS Media_Source,
  {0},
  COUNT(*) AS users
FROM
  `nova-empire-168011.appsflyer_installs_report.af_organic_installs_report`
WHERE
  {1}
GROUP BY
  Media_Source,
  {0}
UNION ALL
SELECT
IF
  (Media_Source = 'restricted',
    'Facebook Ads',
    Media_Source) AS Media_Source,
  {0},
  COUNT(*) AS users
FROM
  `nova-empire-168011.appsflyer_installs_report.af_ins_rep_data`
WHERE
  {1}
GROUP BY
  Media_Source,
  {0}
 """
    # 截取参数
    field_name = arguments[1]
    start_date = arguments[2]
    end_date = arguments[3]
    platform = arguments[5]
    # select,group部分sql
    field_sql = ','.join(FIELD_DICTIONARIES[field_name])

    # where部分sql
    if platform.upper() == PLATFORM_ALL:
        where_sql = """
            DATE(Install_Time,'+08') BETWEEN "{0}" AND "{1}"
        		""".format(start_date, end_date)
    else:
        where_sql = """
        	DATE(Install_Time,'+08') BETWEEN "{0}" AND "{1}" AND Platform = "{2}"	
        		""".format(start_date, end_date, platform.lower())

    install_sql = install_sql.format(field_sql, where_sql)

    client = bq_preparation()

    df = (client.query(install_sql).result().to_dataframe())
    return df


def get_media_retention(arguments: list):
    """根据argument计算不同维度的media留存"""
    # retention前半部分sql
    retention_sql_front = """   
WITH
  result AS (
  SELECT
    'Organic' AS Media_Source,
    {0},
    DATE_DIFF(DATE(A.Event_Time,'+08'), DATE(B.Install_Time,'+08'), DAY) AS delta,
    B.AppsFlyer_ID
  FROM
    `nova-empire-168011.appsflyer_installs_report.af_organic_login` AS A
  INNER JOIN
    `nova-empire-168011.appsflyer_installs_report.af_organic_installs_report` AS B
  ON
    A.AppsFlyer_ID = B.AppsFlyer_ID
    AND A.Install_Time = B.Install_Time
  WHERE
    {1}
  UNION ALL
  SELECT
  IF
    (B.Media_Source = 'restricted',
      'Facebook Ads',
      B.Media_Source),
    {0},
    DATE_DIFF(DATE(A.Event_Time,'+08'), DATE(B.Install_Time,'+08'), DAY) AS delta,
    B.AppsFlyer_ID
  FROM
    `nova-empire-168011.appsflyer_installs_report.af_login` AS A
  INNER JOIN
    `nova-empire-168011.appsflyer_installs_report.af_ins_rep_data` AS B
  ON
    A.AppsFlyer_ID = B.AppsFlyer_ID
    AND A.Install_Time = B.Install_Time
  WHERE
    {1})    
    """
    # 截取参数
    field_name = arguments[1]
    start_date = arguments[2]
    end_date = arguments[3]
    days = arguments[4]
    platform = arguments[5]
    query_type = arguments[6]
    # where部分sql
    if platform.upper() == PLATFORM_ALL:
        where_sql = """
        DATE(B.Install_Time,'+08') BETWEEN "{0}" AND "{1}" 
    		""".format(start_date, end_date)
    else:
        where_sql = """
    	DATE(B.Install_Time,'+08') BETWEEN "{0}" AND "{1}" AND B.Platform = "{2}"
    		""".format(start_date, end_date, platform.lower())

    # select部分sql
    select_sql = ','.join(['B.' + field for field in FIELD_DICTIONARIES[field_name]])

    # 拼接留存前半部分sql
    retention_sql_front = retention_sql_front.format(select_sql, where_sql)

    # 计算查询天数delta
    delta = cal_Max_Dx(start_date, end_date, days)
    # 留存后半部分sql
    retention_sql_end = """
SELECT
  Media_Source,
  {0},
  {1}
FROM
  result
GROUP BY
  Media_Source,
  {0}
  """
    # select,group部分sql
    field_sql = ','.join(FIELD_DICTIONARIES[field_name])

    select_field = ''
    if query_type.lower() == QUERY_TYPE_ALL:
        index = 0
    elif query_type.lower() == QUERY_TYPE_SINGLE:
        index = delta
    while index <= delta:
        select_field += 'COUNT(DISTINCT IF(delta = {0},AppsFlyer_ID,NULL)) AS d{0},'.format(index)
        index += 1

    retention_sql_end = retention_sql_end.format(field_sql, select_field)

    retention_sql = retention_sql_front + retention_sql_end
    client = bq_preparation()

    df = (client.query(retention_sql).result().to_dataframe())
    return df


def get_media_revenue(arguments: list):
    """根据arguments计算不同维度的media收益"""
    revenue_sql_front = """
WITH
  result AS (
  SELECT
    'Organic' AS Media_Source,
    {0},
    DATE_DIFF(DATE(A.Event_Time,'+08'), DATE(B.Install_Time,'+08'), DAY) AS delta,
    A.Event_Revenue_USD
  FROM
    `nova-empire-168011.appsflyer_installs_report.af_organic_purchase` AS A
  INNER JOIN
    `nova-empire-168011.appsflyer_installs_report.af_organic_installs_report` AS B
  ON
    A.AppsFlyer_ID = B.AppsFlyer_ID
    AND A.Install_Time = B.Install_Time
  WHERE
    {1}
  UNION ALL
  SELECT
  IF
    (B.Media_Source = 'restricted',
      'Facebook Ads',
      B.Media_Source),
    {0},
    DATE_DIFF(DATE(A.Event_Time,'+08'), DATE(B.Install_Time,'+08'), DAY) AS delta,
    A.Event_Revenue_USD
  FROM
    `nova-empire-168011.appsflyer_installs_report.af_purchase` AS A
  INNER JOIN
    `nova-empire-168011.appsflyer_installs_report.af_ins_rep_data` AS B
  ON
    A.AppsFlyer_ID = B.AppsFlyer_ID
    AND A.Install_Time = B.Install_Time
  WHERE
    {1})    
        """
    # 截取参数
    field_name = arguments[1]
    start_date = arguments[2]
    end_date = arguments[3]
    days = arguments[4]
    platform = arguments[5]
    query_type = arguments[6]

    # where部分sql
    if platform.upper() == PLATFORM_ALL:
        where_sql = """
            DATE(B.Install_Time,'+08') BETWEEN "{0}" AND "{1}" 
        		""".format(start_date, end_date)
    else:
        where_sql = """
        	DATE(B.Install_Time,'+08') BETWEEN "{0}" AND "{1}" AND B.Platform = "{2}"
        		""".format(start_date, end_date, platform.lower())
    # select部分sql
    select_sql = ','.join(['B.' + field for field in FIELD_DICTIONARIES[field_name]])

    # 拼接revenue前半部分sql
    revenue_sql_front = revenue_sql_front.format(select_sql, where_sql)

    # revenue后半部分sql
    revenue_sql_end = """
 SELECT
  Media_Source,
  {0},
  {1}
FROM
  result
GROUP BY
  Media_Source,
  {0}
  """
    # 计算查询天数delta
    delta = cal_Max_Dx(start_date, end_date, days)

    # select,group部分sql
    field_sql = ','.join(FIELD_DICTIONARIES[field_name])

    select_field = ''
    if query_type.lower() == QUERY_TYPE_ALL:
        index = 0
    elif query_type.lower() == QUERY_TYPE_SINGLE:
        index = delta
    while index <= delta:
        select_field += 'SUM(IF(delta>=0 AND delta<={0},Event_Revenue_USD,0)) AS d{0},'.format(index)
        index += 1
    revenue_sql_end = revenue_sql_end.format(field_sql, select_field)

    revenue_sql = revenue_sql_front + revenue_sql_end
    client = bq_preparation()

    df = (client.query(revenue_sql).result().to_dataframe())
    return df


def get_media_purchase(arguments: list):
    """根据arguments计算不同维度media付费人数"""
    purchase_sql_front = """
WITH
  result AS (
  SELECT
    'Organic' AS Media_Source,
    {0},
    DATE_DIFF(DATE(A.Event_Time,'+08'), DATE(B.Install_Time,'+08'), DAY) AS delta,
    B.AppsFlyer_ID
  FROM
    `nova-empire-168011.appsflyer_installs_report.af_organic_purchase` AS A
  INNER JOIN
    `nova-empire-168011.appsflyer_installs_report.af_organic_installs_report` AS B
  ON
    A.AppsFlyer_ID = B.AppsFlyer_ID
    AND A.Install_Time = B.Install_Time
  WHERE
    {1}
  UNION ALL
  SELECT
  IF
    (B.Media_Source = 'restricted',
      'Facebook Ads',
      B.Media_Source),
    {0},
    DATE_DIFF(DATE(A.Event_Time,'+08'), DATE(B.Install_Time,'+08'), DAY) AS delta,
    B.AppsFlyer_ID
  FROM
    `nova-empire-168011.appsflyer_installs_report.af_purchase` AS A
  INNER JOIN
    `nova-empire-168011.appsflyer_installs_report.af_ins_rep_data` AS B
  ON
    A.AppsFlyer_ID = B.AppsFlyer_ID
    AND A.Install_Time = B.Install_Time
  WHERE
    {1})
        """
    # 截取参数
    field_name = arguments[1]
    start_date = arguments[2]
    end_date = arguments[3]
    days = arguments[4]
    platform = arguments[5]
    query_type = arguments[6]
    # where部分sql
    if platform.upper() == PLATFORM_ALL:
        where_sql = """
            DATE(B.Install_Time,'+08') BETWEEN "{0}" AND "{1}" 
        		""".format(start_date, end_date)
    else:
        where_sql = """
        	DATE(B.Install_Time,'+08') BETWEEN "{0}" AND "{1}" AND B.Platform = "{2}"
        		""".format(start_date, end_date, platform.lower())

    # select部分sql
    select_sql = ','.join(['B.' + field for field in FIELD_DICTIONARIES[field_name]])

    # 拼接purchase前半部分sql
    purchase_sql_front = purchase_sql_front.format(select_sql, where_sql)

    # purchase后半部分sql
    purchase_sql_end = """
SELECT
  Media_Source,
  {0},
  {1}
FROM
  result
GROUP BY
  Media_Source,
  {0}
    """
    # 计算查询天数delta
    delta = cal_Max_Dx(start_date, end_date, days)

    # select,group部分sql
    field_sql = ','.join(FIELD_DICTIONARIES[field_name])

    select_field = ''
    if query_type.lower() == QUERY_TYPE_ALL:
        index = 0
    elif query_type.lower() == QUERY_TYPE_SINGLE:
        index = delta
    while index <= delta:
        select_field += 'COUNT(DISTINCT IF(delta >=0 AND delta <= {0},AppsFlyer_ID,NULL)) AS d{0},'.format(index)
        index += 1

    purchase_sql_end = purchase_sql_end.format(field_sql, select_field)

    purchase_sql = purchase_sql_front + purchase_sql_end
    client = bq_preparation()

    df = (client.query(purchase_sql).result().to_dataframe())
    return df


def get_media_country_install_filtered(date_start: str, date_end: str, platform_str: str):
    install_sql = """
SELECT
  "Organic" AS Media_Source,
  A.Country_Code,
  COUNT(DISTINCT A.AppsFlyer_ID) AS users
FROM
  `nova-empire-168011.appsflyer_installs_report.af_organic_installs_report` AS A
INNER JOIN
  `nova-empire-168011.appsflyer_installs_report.af_organic_login` AS B
ON
  A.AppsFlyer_ID = B.AppsFlyer_ID
  AND A.Install_Time = B.Install_Time
INNER JOIN
  `nova-empire-168011.appsflyer_installs_report.uid_regist_ts` AS C
ON
  B.Customer_User_ID = C.uid
WHERE
  {0}
GROUP BY
  1,
  2
UNION ALL
SELECT
IF
  (A.Media_Source = 'restricted',
    'Facebook Ads',
    A.Media_Source),
  A.Country_Code,
  COUNT(DISTINCT A.AppsFlyer_ID) AS users
FROM
  `nova-empire-168011.appsflyer_installs_report.af_ins_rep_data` AS A
INNER JOIN
  `nova-empire-168011.appsflyer_installs_report.af_login` AS B
ON
  A.AppsFlyer_ID = B.AppsFlyer_ID
  AND A.Install_Time = B.Install_Time
INNER JOIN
  `nova-empire-168011.appsflyer_installs_report.uid_regist_ts` AS C
ON
  B.Customer_User_ID = C.uid
WHERE
  {0}
GROUP BY
  1,
  2 
    """
    if platform_str.upper() == PLATFORM_ALL:
        temp_sql = """
        DATE(A.Install_Time,'+08') BETWEEN "{0}" AND "{1}" AND C.ts >= A.Install_Time
    		""".format(date_start, date_end)

        install_sql = install_sql.format(temp_sql)
    else:
        temp_sql = """
    	DATE(A.Install_Time,'+08') BETWEEN "{0}" AND "{1}" AND A.Platform = "{2}" AND C.ts >= A.Install_Time
    		""".format(date_start, date_end, platform_str.lower())

        install_sql = install_sql.format(temp_sql)

    client = bq_preparation()

    df = (client.query(install_sql).result().to_dataframe())
    return df
