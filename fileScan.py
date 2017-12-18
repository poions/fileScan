# -*- coding:utf-8 -*-
import os
import re
import sys
import time
import math
import Queue
import requests
import threading
from fileScan import *
from controller import *
import libs.requests as requests

class fileScan(object):
	def __init__(self,url,ext):
		self.timeout = 5
		self.headers = {
			"Accept":"text/html,application/xhtml+xml,application/xml;",
			"Accept-Encoding":"gzip",
			"Accept-Language":"zh-CN,zh;q=0.8",
			"Referer":"https://www.baidu.com/",
			"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
		}
		self.url_keyword_file = 'page/url_keyword2.dict'				
		self.file_keyword_file = 'page/file_keyword2.dict'				
		self.thread_num = 10									#设置线程数
		self.save_url_keywords = ['']
		self.scan_level = -1
		self.bak_ext = ['zip','rar','tar','tar.gz','sql']				#备份文件格式
		self.STOP_FILE = False #禁止文件扫描
		self.STOP_URL = False  #禁止目录扫描
		self.msg_queue = Queue.Queue()
		self.STOP_ME = False
		self.scan_level = 2
		self.target_url = url
		self.file_ext = str(ext)
		
		
	def _req_code(self,url):
		url = url if url[:4] == 'http' else 'http://' + url
		try:
			req = requests.get(url,headers=self.headers,timeout=self.timeout)
			code = req.status_code
		except Exception, e:
			code = 520
			print e
		return code
		
	def _check_404(self,url):
		url = url+ "/check_404_" + str(int(time.time()))
		code = self._req_code(url)
		if code == 520:
			print "network error!!"
		else:
			return True
			
	def _get_urlkeyword(self):
		f = open(self.url_keyword_file, 'r')
		url_keywords = f.readlines()
		f.close()
		return [i.strip() for i in url_keywords]
	
	def _get_filekeyword(self):
		f = open(self.file_keyword_file,'r')
		file_keywords = f.readlines()
		f.close()
		return [i.strip() for i in file_keywords]
		
	def saveKey_and_urlKey(self,keywords):
		"""合成扫描路径字典"""
		and_keys = []
		urlkeys = self._get_urlkeyword()
		for uk in urlkeys:
			for sk in keywords:
				and_keys.append(sk+'/'+uk)
		return and_keys
		
		
	def saveKey_and_fileKey(self,keywords):
		"""合成扫描文件字典"""
		and_keys = []
		filekeys = self._get_filekeyword()
		for fk in filekeys:
			for sk in keywords:
				and_keys.append(sk+'/'+fk+'.'+self.file_ext)
		for sk in keywords: 
			for ext in self.bak_ext:
				and_keys.append(sk+'/'+sk.split('/')[-1]+'.'+ext)			#存储备份文件
		return and_keys 
		
	def url_keyword_scan(self,keywords):
		for key in keywords:
			key = key.strip()
			#print key
			url = self.target_url + key if self.target_url[-1] == '/' or key[0] == '/' else self.target_url + '/' + key
			#print url         #拼接成完整url
			code = self._req_code(url)
			print str(code)+" "+str(url)
			if int(code) in [200,403]:
				self.msg_queue.put('true'+url)
				#将结果写入文本
				with open("result.txt",'a+') as files:
					files.write(url+"\n")
					start_wyspider(url)							#将url调使给爬扫
				if url.split('/')[-1].find('.') == -1:
					self.save_url_keywords.append(key)

	def function_scan(self,url,ext='php'):
		if self._check_404(url):
			print "not error!!"
		else:
			exit()
		while (len(self.save_url_keywords) > 0 and self.scan_level != 0):
			file_keywords = self.saveKey_and_fileKey(self.save_url_keywords)
			#print file_keywords
			url_keywords = self.saveKey_and_urlKey(self.save_url_keywords)
			#print url_keywords
			if self.STOP_FILE:
				scan_list = url_keywords
				#print scan_list
			elif self.STOP_URL:
				scan_list = file_keywords
				#print scan_list
				self.scan_level = 1
			else:
				scan_list = url_keywords+file_keywords				#字典组合
			self.save_url_keywords = []
			self.scan_level = self.scan_level - 1
			count = math.ceil(len(scan_list)/self.thread_num)
			count = int(count)
			thread_list = []
			for n in range(self.thread_num+1):
				#print n
				thread_list.append(threading.Thread(target=self.url_keyword_scan,args=(scan_list[n*count:(n+1)*count],)))
			for t in thread_list:
				t.start()
			for t in thread_list:
				t.join()
			self.STOP_ME = True
		
if __name__=='__main__':
	ext_list = ['php','asp','jsp','aspx']
	input_url = sys.argv[1:][0]
	input_ext = sys.argv[1:][1]
	if input_ext not in ext_list:
		print "[!]error:-->%s" % (input_ext)
		exit(0)
	else:
		pass
	s = fileScan(input_url,input_ext)
	s.function_scan(input_url,input_ext)
