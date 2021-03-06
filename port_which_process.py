#!/usr/bin/env python3

import os
import sys


def getcmdoutput(cmd):
    """ execectue cmd, and give back output lines as array """
    with os.popen(cmd) as p:
        outputlines = p.readlines()
    return outputlines




def what_on_port(myport):

	myport = str(myport)
	name = None

	cmd = 'netstat -apon 2>&1 | grep tcp | grep LISTEN'
	for thisline in getcmdoutput(cmd):
		# Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name     Timer
		# tcp        0      0 0.0.0.0:8080            0.0.0.0:*               LISTEN      500183/python3       off (0.00/0/0)
		# tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                    off (0.00/0/0)

		ipport = thisline.split()[3]
		pidprogname = thisline.split()[6]

		if ipport.endswith(":" + myport):
			if pidprogname == "-":
				name = "process owned by other user"
			else:
				name = pidprogname
				
	return(name)
	
	
myport = sys.argv[1]
process = what_on_port(myport)
if process:
	print("yes, port in use by", process)
else:
	print("port not in use")
	


