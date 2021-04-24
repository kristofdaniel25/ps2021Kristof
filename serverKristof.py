#!/usr/bin/env python3.9
import socket
import os
import sys
import signal

class Status:
	def __init__(self,stat_num,stat_name):
		self.num=stat_num
		self.name=stat_name
	def send_status(self,f):
		f.write(str(self.num) +' '+ self.name +'\n')

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('',9999))
signal.signal(signal.SIGCHLD,signal.SIG_IGN)
s.listen(5)
commands=['READ\n','WRITE\n','LS\n']

while True:
	connected_socket,address=s.accept()
	print(f'spojene, adresa:',address)
	pid_chld=os.fork()
	current_status=Status(200,'Bad request')
	if pid_chld == 0:
		s.close()
		f=connected_socket.makefile(mode='rw',encoding='utf-8')
		data=f.readline()
		if data in commands:
			print(f'YES, data prijate:',data) #VYMAZAT
			f.flush()		
			while True:
				data=f.readline()
				print("data prijate: ",data)
				if not data:
					break
				f.write('PONG\n')
				a=Status(203,'Unknown Error')
				a.send_status(f)
				f.flush()
		else:
			current_status.send_status(f)
		print(f'spojenie uzavrete s adresou', address)
		sys.exit(0)
	else:
		connected_socket.close()











