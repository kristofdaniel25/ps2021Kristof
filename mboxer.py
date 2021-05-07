#!/usr/bin/env python3.9
import socket
import os
import sys
import signal
import hashlib
import os.path
from os import path

class Status:
	def __init__(self,stat_num,stat_name):
		self.num=stat_num
		self.name=stat_name
	def set(self,new_num,new_name):
		self.num=new_num
		self.name=new_name
	def send_status(self,f):
		f.write(str(self.num) +' '+ self.name +'\n')
		f.flush()
class Header:
	def __init__(self,list_of_elem):
		self.id=list_of_elem[0]
		self.value=list_of_elem[1].strip('\n')
	def send_header(self,f):
		f.write(self.id +' '+ self.value +'\n')
		f.flush()

def set_header(raw_string): #sluzi na pripravu suroveho textu pre konstruktor triedy Header
	elem=raw_string.split(':')
	ret_list=[]
	if len(elem)==2:
		if (elem[0].isascii()):
			if (' ' not in elem[0] and '/' not in elem[0] and '/' not in elem[1]):
				ret_list=elem
	return ret_list		
			
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('',9999))
signal.signal(signal.SIGCHLD,signal.SIG_IGN)
s.listen(5)
commands=['READ\n','WRITE\n','LS\n']

while True:
	connected_socket,address=s.accept()
	pid_chld=os.fork()
	current_status=Status(200,'Bad request')
	if pid_chld == 0:
		while True:
			s.close()
			header1=[]
			header2=[]
			data=''
			current_status.set(200,'Bad request')
			f=connected_socket.makefile(mode='rw')
			data=f.readline()
			if data in commands:
				if (commands.index(data)==0): #READ
					while True:
						data=f.readline()
						header1=set_header(data)
						if (len(header1)==2 and header1[0] == 'Mailbox'):	#ak su tie dve casti hlavicky v poriadku,
							mailbox_head=Header(header1)			#robim z nich prvok triedy Header
							data=f.readline()
							header2=set_header(data)
							if (header2[0]=='Message'):
								message_head=Header(header2)
								if not path.exists(mailbox_head.value):
									current_status.set(201,'No such message')
									current_status.send_status(f)	
									break
								with open(mailbox_head.value+'/'+message_head.value) as my_file:
									content=my_file.read()
								current_status.set(100,'OK')
								current_status.send_status(f)	
								f.write('Content-length:'+str(len(content)))
								f.flush()
								f.write('\n'+content+'\n')
								f.flush()
								break
							else:
								current_status.send_status(f)
								break			
						else:
							current_status.send_status(f)
							break
				elif (commands.index(data)==1): #WRITE
					while True:
						data=f.readline()
						header1=set_header(data)
						if (len(header1)==2 and header1[0] == 'Mailbox'):
							mailbox_head=Header(header1)
							data=f.readline()
							header2=set_header(data)
							if (header2[0]=='Content-length' and int(header2[1])>-1):
								cont_len=Header(header2)
								if not path.exists(mailbox_head.value):
									current_status.set(203,'No such mailbox')
									current_status.send_status(f)
									break
								else:
									m=hashlib.md5()
									current_status.set(100,'OK')
									message=f.readline(int(cont_len.value))
									hex_path=m.hexdigest()
									f.flush()
									with open(mailbox_head.value+'/'+hex_path,"w") as my_file:
										my_file.write(message)
									current_status.send_status(f)
									break
							else:
								current_status.send_status(f)
								break
						else:
							current_status.send_status(f)
							break
				elif (commands.index(data)==2): #LS
					while True:
						data=f.readline()
						header1=set_header(data)
						if (len(header1)==2 and header1[0] == 'Mailbox'):
							mailbox_head=Header(header1)
							if not path.exists(mailbox_head.value):
								current_status.set(201,'No such mailbox')
								break
							files_list=[]
							files_list=os.listdir(mailbox_head.value)
							current_status.set(100,'OK')
							current_status.send_status(f)		
							f.write('Number-of-messages:'+str(len(files_list))+'\n')
							f.flush()
							for item in files_list:
								f.write(item+'\n')
								f.flush()
							break
						else:
							current_status.send_status(f)
							break
			else:
				current_status.set(204,'Unknown method')
				current_status.send_status(f)
sys.exit(0)










