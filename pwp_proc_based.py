#!/usr/bin/env python3

'''
on Linux, given a certain, find if in use, and if so, by which process ... without using netstat

'''

import os
import sys
import glob

def to4hex(number):
	return ('0000' + hex(number).replace("0x","").upper())[-4:]

'''

$ cat /proc/net/tcp 
  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode                                                     
   0: 00000000:2008 00000000:0000 0A 00000000:00000000 00:00000000 00000000   131        0 43850 1 0000000000000000 100 0 0 10 0                     
   1: 0100007F:8A69 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 35206 1 0000000000000000 100 0 0 10 0                     
   2: 00000000:008B 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 42930 1 0000000000000000 100 0 0 10 0                     
   3: 00000000:1F90 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 7554459 1 0000000000000000 100 0 0 10 0  
  25: 3802A8C0:C8E4 0302A8C0:1F49 01 00000000:00000000 02:00000D3E 00000000  1000        0 7717199 2 0000000000000000 22 4 30 7 7                    
  26: 3802A8C0:BD4E 05D63AD8:01BB 06 00000000:00000000 03:000005AD 00000000     0        0 0 3 0000000000000000   
  
$ cat /proc/net/tcp6
  sl  local_address                         remote_address                        st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
   0: 00000000000000000000000000000000:1F40 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 45488 1 0000000000000000 100 0 0 10 0
   1: 00000000000000000000000000000000:2328 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 44644 1 0000000000000000 100 0 0 10 0
   2: 00000000000000000000000000000000:008B 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 42928 1 0000000000000000 100 0 0 10 0
   3: 00000000000000000000000000000000:0050 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 34397 1 0000000000000000 100 0 0 10 0
   4: 00000000000000000000000000000000:0016 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 35036 1 0000000000000000 100 0 0 10 0
   5: 00000000000000000000000001000000:0277 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 6863491 1 0000000000000000 100 0 0 10 0
   6: 00000000000000000000000000000000:075B 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 43564 1 0000000000000000 100 0 0 10 0


'''

def port2info(myport):
	myporthex = to4hex(myport)
	# Check TCP ports on IPv4, then IPv6:
	for filepath in ['/proc/net/tcp', '/proc/net/tcp6']:
		with open(filepath) as fp:
			for cnt, line in enumerate(fp):
				if line.find("00000000:0000 ") >= 0 and line.find(":" + myporthex) >= 0:
					# Yes, listening process, on the port we're looking for 

					#local_address = line.split()[1]
					uid = line.split()[7]
					inode = line.split()[9]
					#hexaddress, hexport = local_address.split(':')
					#decport = int(hexport, 16)
					return uid, inode
	return None, None
			

def inode2pid(inode):
	# we search the whole /proc/*/fd/* for a symlink pointing to a socket with the inode given
	# ... and we return the PID of the owning process
	# for example: searching for inode 7554459, we'll return pid 500183
	# /proc/500183/fd/12 -> 'socket:[7554459]'

	# Create the 'socket:[7554459]'
	searchfor = 'socket:[' + str(inode) + ']'
	for myfile in glob.glob('/proc/*/fd/*'):
		try:
			bla = os.readlink(myfile)
			if bla.find(searchfor) >= 0:
				pid = myfile.split('/')[2]
				return pid
		except:
			pass
	return None

def port2pid(myport):
	uid, inode = port2info(myport)
	if inode:
		# find owning proces of that inode
		pidfound = inode2pid(inode)
		if pidfound:
			return pidfound
		else:
			# this is weird!
			return -1
	else:
		return None


myport = int(sys.argv[1])
pid = port2pid(myport)
if pid and pid >= 0:
	print("Port", myport, "used by pid", pid)
else:
	print("Port", myport, "not in use")


	
	


