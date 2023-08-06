##########################################################################################################################################################################
# the import lib block
##########################################################################################################################################################################
from multiprocessing import Pool


##########################################################################################################################################################################
# the Constant block
##########################################################################################################################################################################


##########################################################################################################################################################################
# the function block
##########################################################################################################################################################################
def gb_process_pool_disposable(pro_num: int, call_back_func, tuple_list: list):
	"""
	this function is block to wait all the job accompulished!!!
	:param pro_num: usually use physical CPU number
	:param call_back_func: job function
	:param tuple_list: eg: [(), (), (), (), (), (), (), (), ......]
	:return: None
	"""
	po = Pool(pro_num)  # define a process pool, assign processNumbers
	for tup in tuple_list:
		po.apply_async(call_back_func, tup)

	print("----start process pool num[{}]----".format(pro_num))
	po.close()  # close pool, don't accept new process task
	po.join()   # wait for all the task accompulished
	print("-----end process pool -----")


class GbProcessPool:
	"""
	persistent process pool
	"""
	def __init__(self, proc_num: int):
		print("----starting process pool num[{}]----".format(proc_num))
		self.po = Pool(proc_num)
		print("----starting process pool finished----")

	def add_proc_to_pool(self, callback_func, param_of_tup: tuple):
		self.po.apply_async(callback_func, param_of_tup)

	def destroy_proc_pool(self):
		self.po.close()  # close pool, don't accept new process task
		self.po.join()   # wait for all the task accompulished
		print("-----end process pool -----")
