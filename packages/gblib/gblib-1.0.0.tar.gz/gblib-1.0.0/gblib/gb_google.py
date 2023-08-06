##########################################################################################################################################################################
# the import lib block
##########################################################################################################################################################################
from google.cloud import bigquery
from gblib.gb_time import *

##########################################################################################################################################################################
# the Constant block
##########################################################################################################################################################################
BQ_TIMEOUT = 240
BQ_THREAD_DRY_RUN_LIMIT = 20  # https://cloud.google.com/bigquery/quotas#queries        #max is 100 per project
BQ_QUERY_SLEEP_SECONDS = 1

BQ_DATASET_ID = 'appsflyer_installs_report'
BQ_DATASET_APP_EVENT_ID = 'analytics_151058707'
BQ_DATASET_TEST_ID = 'operation_test_tmp'

BQ_TABLE_ID = 'server_data'
BQ_DOMESTIC_TABLE_ID = 'server_data_domestic'

AUTH_JSON_FILE_PATH = '/bigquery/script/pythonCode/Nova_Empire-b994b58869d3.json'
AUTH_WHOLE_JSON_FILE_PATH = '/bigquery/script/pythonCode/nova-empire-168011-c04d361df9af_wholeProj.json'
PROJECT = 'nova-empire-168011'
GCS_URL_PREFIX = 'gs://bigdata_bak/afToBq/'
BACKUP_FILE_PREFIX = '/bigquery/yy/'


##########################################################################################################################################################################
# the function block
##########################################################################################################################################################################
def bq_preparation(if_modify=False):
	if if_modify == False:
		return bigquery.Client.from_service_account_json(AUTH_JSON_FILE_PATH)
	elif if_modify == True:
		return bigquery.Client.from_service_account_json(AUTH_WHOLE_JSON_FILE_PATH)
	else:
		print('bq_preparation parameter error!')
		return False


def bq_get_tables(tabList, dataset):
	bq_client = bq_preparation()
	dataset_ref = bq_client.dataset(dataset)
	tables = list(bq_client.list_tables(dataset_ref))

	for i in tables:
		tabList.append(str(i.table_id))


def bq_check_tb_in_dataset(dStr, tabStr):
	tableList = []
	bq_get_tables(tableList, dStr)
	if tabStr in tableList:
		print('find bq talbe in dataset:' + dStr)
	else:
		return False

	return True


def bq_create_dataset(dataset_str):
	# Use to creat dataset, dataset_str: name of the dataset
	bq_client = bq_preparation()

	dataset_ref = bq_client.dataset(dataset_str)
	dataset = bigquery.Dataset(dataset_ref)
	bq_client.create_dataset(dataset)
	print('Created dataset: {}'.format(dataset_str))


'''
schema example:
schema = [
		bigquery.SchemaField(KEY_TS, 		'TIMESTAMP',	mode = 'REQUIRED'),
		bigquery.SchemaField(KEY_CMD, 		'STRING', 		mode = 'REQUIRED'),
		bigquery.SchemaField(KEY_UID, 		'STRING', 		mode = 'NULLABLE'),
		bigquery.SchemaField(KEY_SERVER, 	'STRING', 		mode = 'NULLABLE'),
		bigquery.SchemaField(KEY_PLATFORM, 	'STRING', 		mode = 'NULLABLE'),
		bigquery.SchemaField(KEY_LEVEL, 	'INTEGER', 		mode = 'NULLABLE'),
		bigquery.SchemaField(KEY_PARAMS, 	'RECORD', 		mode = 'REPEATED', fields=[
			bigquery.SchemaField(KEY_PARAMS_VN, 	'STRING',	mode = 'NULLABLE'),
			bigquery.SchemaField(KEY_PARAMS_STR, 	'STRING',	mode = 'NULLABLE'),
			bigquery.SchemaField(KEY_PARAMS_INT, 	'INTEGER',	mode = 'NULLABLE'),
			bigquery.SchemaField(KEY_PARAMS_FLOAT, 	'FLOAT',	mode = 'NULLABLE'),
		]),
	]
'''


def bq_create_partition_table(dataset_id, table_id, schema, field_key):
	bigquery_client = bigquery.Client.from_service_account_json(AUTH_WHOLE_JSON_FILE_PATH)
	dataset_ref = bigquery_client.dataset(dataset_id)
	table_ref = dataset_ref.table(table_id)

	table = bigquery.Table(table_ref, schema=schema)

	table.time_partitioning = bigquery.TimePartitioning(
		type_=bigquery.TimePartitioningType.DAY,
		field=field_key  # name of column to use for partitioning
	)

	table = bigquery_client.create_table(table)
	print('Created table {}, partitioned on column {}'.format(table.table_id, table.time_partitioning.field))


def bq_create_normal_table(datasetStr, tableStr, schemaList):
	bq_client = bq_preparation()
	dataset_ref = bq_client.dataset(datasetStr)

	table_ref = dataset_ref.table(tableStr)
	table = bigquery.Table(table_ref, schema=schemaList)
	table = bq_client.create_table(table)
	print('create %s' % table.table_id, 'success!')


def bq_del_table(datasetStr, tableStr):
	importantTableList = [
		'af_ins_rep_data',
		'buyFirstBuy',
		'missionCollect3Level',
		'operation_fragmentInfo',
		'operation_itemInfo',
		'operation_modelMaterialInfo',
		'operation_openCrate',
		'operation_rankingInfo',
		'operation_unionInfo',
		'planning_BeginRandomMission',
		'planning_FIGHT_POWER',
		'sceneDuration_uid_dDate',
		'server_data',
		'sub_ReqGetBuyResult',
		'trackId_fstOpen_dup',
		'trackId_inAppPurchase',
		'trackId_sceneDuration',
		'trackId_uid_sceneDuration',
		'uid_inAppPurchase',
		'voidedPurchase',
	]

	if tableStr in importantTableList:
		return

	bq_client = bq_preparation()
	dataset_ref = bq_client.dataset(datasetStr)
	table_ref = dataset_ref.table(tableStr)
	deleted = bq_client.delete_table(table_ref)


def run_query(bqSql, if_modify=False):
	if if_modify == False:
		client = bq_preparation()
	elif if_modify == True:
		client = bq_preparation(True)
	else:
		print('run_query parameter error!')
		return False

	# print(bqSql)
	query_job = client.query(bqSql)

	bqListRet = list(query_job.result(timeout=BQ_TIMEOUT))  # Waits for job to complete.
	return bqListRet


def load_file_to_bq(dataset_id, table_id, source_file_name):
	bigquery_client = bq_preparation()

	dataset_ref = bigquery_client.dataset(dataset_id)
	table_ref = dataset_ref.table(table_id)

	with open(source_file_name, 'rb') as source_file:
		# This example uses CSV, but you can use other formats.
		# See https://cloud.google.com/bigquery/loading-data
		job_config = bigquery.LoadJobConfig()
		if source_file_name.endswith('.json'):
			job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
		else:
			job_config.source_format = 'text/csv'
		job = bigquery_client.load_table_from_file(source_file, table_ref, job_config=job_config)
	if source_file_name.endswith('.json'):
		print('Starting job {} json{}'.format(job.job_id, source_file_name))
	job.result()  # Waits for job to complete
	print('Loaded {} rows into {}:{}.'.format(job.output_rows, dataset_id, table_id))


def cpGcsToLocal(gcs_file_url, local_file_prefix):
	"""
		copy csv on gcs to local
	:param gcs_file_url: gcs file path
	:param local_file_prefix: local file prefix
	:return: local csv url if succeed else None
	"""
	print('Starting copying')
	local_url = local_file_prefix + gcs_file_url.split('/')[-1]

	try:
		os.system('gsutil cp -p ' + gcs_file_url + ' ' + local_url)
		print('Copied file from ' + gcs_file_url + ' to ' + local_url)
		return local_url
	except Exception:
		print('Failed while copying ' + gcs_file_url + ' to local')
	return None


def cpLocalToGcs(local_file_url, gcs_url_prefix):
	"""
		copy csv on local to gcs
	:param local_file_url: local file name
	:param gcs_url_prefix: gcs path prefix
	:return: gcs url if succeed else None
	"""
	if not os.path.exists(local_file_url):
		print('File ' + local_file_url + 'does not exist')
		return

	destination_uri = gcs_url_prefix + os.path.basename(local_file_url)
	try:
		os.system('gsutil cp ' + local_file_url + ' ' + destination_uri)
		print('Copied ' + local_file_url + ' to gs')
		return destination_uri
	except Exception:
		print('Failed while copying ' + local_file_url + ' to gs')
	return None
