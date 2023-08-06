import sqlite3
import pymysql

DB_SQLITE   = 'sqlite'
DB_MYSQL    = 'mysql'

MYSQL_HOST      = 'localhost'
MYSQL_USER      = 'root'
MYSQL_PASSWORD  = '!yxcy#0105'
MYSQL_PORT      = 52036


class SqliteConnector:
	def __init__(self, p_tup):
		self.conn = sqlite3.connect(p_tup[0])
		self.cur = self.conn.cursor()

	def run_query(self, sql, if_commit = False):
		query_ret = self.cur.execute(sql)
		if if_commit:
			self.conn.commit()
		return list(query_ret)

	def execute_query(self, *args, if_commit = False, **kwargs):
		query_ret = self.cur.execute(*args, **kwargs)
		if if_commit:
			self.conn.commit()
		return list(query_ret)

	def __del__(self):
		self.cur.close()
		self.conn.close()


class MysqlConnector:
	def __init__(self, p_tup):
		self.conn = pymysql.connect(host = p_tup[0], user = p_tup[1], password = p_tup[2], database = p_tup[3], port = p_tup[4])
		self.cur = self.conn.cursor()

	def run_query(self, sql, if_commit = False):
		self.cur.execute(sql)
		query_ret = self.cur.fetchall()
		if if_commit:
			self.conn.commit()
		return list(query_ret)

	def __del__(self):
		self.cur.close()
		self.conn.close()


def _connection_factory(db_tp, param_tup):
	if db_tp == DB_SQLITE:
		connector = SqliteConnector
	elif db_tp == DB_MYSQL:
		connector = MysqlConnector
	else:
		raise ValueError('Cannot connect to db_param_tup[{1}]. db type[{0}] and path do not match!'.format(db_type, param_tup))
	return connector(param_tup)


# if Sqlite, param_tup: (db_path)
# if Mysql, param_tup: (host, user_name, password, database_name, port)
def connect_db(db_type, param_tup):
	conn = None
	try:
		conn = _connection_factory(db_type, param_tup)
	except Exception as e:
		print(e)
	return conn

# db_hd = connect_db(DB_SQLITE, (REPAIR_FB_DB_PATH, ))
# db_hd = connect_db(DB_MYSQL, ("localhost", "root", '!yxcy#0105', 'testmysql', 52036))
