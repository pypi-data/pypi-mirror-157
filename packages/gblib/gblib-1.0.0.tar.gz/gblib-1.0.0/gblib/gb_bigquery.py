# -*- coding: utf-8 -*-
# @Time    : 2020/8/12 10:30
# @Author  : SongWei

import logging
import os
import re

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from gblib.gb_common import GbConfig, OPERATION_MAIL_LIST, ADMIN_MAIL_LIST
from gblib.gb_net import send_email

config = GbConfig()
logging.basicConfig(level=logging.INFO)


class BigQuery:
	def __init__(self, project_name: str):
		"""
		:param project_name: 项目名称， 根据config文件中的section名确定
		"""
		self.project_name = project_name

		self.project_id = config.get(project_name, 'PROJECT_ID')
		self._credential_wr = config.get(project_name, 'CREDENTIAL_PATH_WR')
		self._client_wr = bigquery.Client.from_service_account_json(self._credential_wr)  # 读写权限

	def is_table_in_dataset(self, dataset_name: str, table_name: str):
		"""
		检查数据集中是否有该表
		"""
		dataset = self._client_wr.get_dataset(self.project_id + '.' + dataset_name)
		tables = [x.table_id for x in self._client_wr.list_tables(dataset)]
		return table_name in tables

	def create_dataset(self, dataset_name: str):
		"""创建数据集"""
		dataset = bigquery.Dataset(self.project_id + '.' + dataset_name)
		self._client_wr.create_dataset(dataset)
		logging.info('Created dataset: {}'.format(dataset_name))
		return True

	def create_table(self, dataset_name: str, table_name: str, schema: str, partition_key: str = None):
		"""
		创建创建分区表
		:param dataset_name:  数据集name
		:param table_name:  表名
		:param schema: 表结构
			schema = [
			bigquery.SchemaField('ts', 		'TIMESTAMP',	mode = 'REQUIRED'),
			bigquery.SchemaField('cmd, 		'STRING', 		mode = 'REQUIRED'),
			bigquery.SchemaField('uid, 		'STRING', 		mode = 'NULLABLE'),
			bigquery.SchemaField('params', 	'RECORD', 		mode = 'REPEATED',
				fields=[
					bigquery.SchemaField('vn', 	'STRING',	mode = 'NULLABLE'),
					bigquery.SchemaField('str', 	'STRING',	mode = 'NULLABLE'),
				])
			]
		:param partition_key: 需要分区的字段，按天分区，不填则不需要分区
		"""
		table_id = '.'.join([self.project_id, dataset_name, table_name])
		table = bigquery.Table(table_id, schema=schema)
		if partition_key:
			table.time_partitioning = bigquery.TimePartitioning(type_=bigquery.TimePartitioningType.DAY, field=partition_key)

		table = self._client_wr.create_table(table)
		logging.info('Created table {}'.format(table.table_id))
		return True

	def run_query(self, sql: str, write: bool = False):
		"""
		使用查询bigquery库的方法查询数据，返回的是[Row(), Row()]的列表
		:param sql: 需要查询的sql
		:param write: 该查询是否需要写入权限，该参数主要是提醒操作者可能会对数据库造成损害。
		:return:
		"""
		logging.debug(sql)
		if write:
			query_job = self._client_wr.query(sql)
		else:
			query_job = self._client_wr.query(sql)

		try:
			return list(query_job.result(timeout=int(config.get('BASIC', 'BQ_TIMEOUT'))))  # Waits for job to complete.
		except Exception as e:
			send_email('bigquery查询异常', f'error sql[{sql}]\nexception[{e}]', ADMIN_MAIL_LIST, 'DATA RECEIVER')
			exit()

	def run_query_with_pandas(self, sql):
		"""
		使用pandas.read_gbq查询数据，返回dataframe，只读，无法删除或插入数据
		"""
		credentials = service_account.Credentials.from_service_account_file(self._credential_wr)
		df = pd.read_gbq(sql, project_id=self.project_id, credentials=credentials, dialect='standard', progress_bar_type='tqdm')
		return df

	def load_file_to_bq(self, dataset_name: str, table_name: str, source_file_path: str):
		"""
		上传文件到bigquery中
		"""
		table_id = '.'.join([self.project_id, dataset_name, table_name])
		table_ref = self._client_wr.get_table(table_id)

		if not os.path.exists(source_file_path):
			raise Exception('source file is not exist')

		try:
			with open(source_file_path, 'rb') as source_file:
				# This example uses CSV, but you can use other formats.
				# See https://cloud.google.com/bigquery/loading-data
				job_config = bigquery.LoadJobConfig()
				if source_file_path.endswith('.json'):
					job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
				else:
					job_config.source_format = 'text/csv'
				job = self._client_wr.load_table_from_file(source_file, table_ref, job_config=job_config)
			job.result()  # Waits for job to complete
			logging.info('Loaded {} rows into {}:{}.'.format(job.output_rows, dataset_name, table_name))
		except Exception as e:
			# send_email('bigquery load_file_to_bq异常', f'dataset_name[{dataset_name}] table_name[{table_name}] source_file_path[{source_file_path}] \nexception[{e}]', ADMIN_MAIL_LIST, 'DATA RECEIVER')
			return False
		return True

	def del_table(self, dataset_name: str, table_name: str):
		"""删除表"""
		table_id = '.'.join([self.project_id, dataset_name, table_name])
		if not self._client_wr.get_table(table_id):
			raise Exception('table is not exist')
		important_table_list = re.sub(r'\s', '', config.get(self.project_name, 'IMPORTANT_TABLE_NAME')).split(',')
		if table_name in important_table_list:
			raise Exception('This table is important, forbid delete')

		self._client_wr.delete_table(table_id)
		logging.info('delete table {}.{}'.format(dataset_name, table_name))
		return True


def cpGcsToLocal(gcs_file_url, local_file):
	"""
		copy csv on gcs to local
	:param gcs_file_url: gcs file path
	:param local_file: local file prefix
	:return: local csv
	"""
	logging.info('Starting copying')
	os.system('gsutil cp -p {} {}'.format(gcs_file_url, local_file))
	logging.info('Copied file from {} to {}'.format(gcs_file_url, local_file))
	return local_file


def cpLocalToGcs(local_file_url, gcs_url):
	"""
		copy csv on local to gcs
	:param local_file_url: local file name
	:param gcs_url: gcs path prefix
	:return: gcs url
	"""
	if not os.path.exists(local_file_url):
		raise Exception('File {} does not exist'.format(local_file_url))
	os.system('gsutil cp {} {}'.format(local_file_url, gcs_url))
	logging.info('Copied {} to gs'.format(local_file_url))
	return gcs_url


if __name__ == '__main__':
	bq = BigQuery('NOVA')
