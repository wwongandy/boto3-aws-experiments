#!/usr/bin/env python3

## Importing the subprocess library to run shell commands via python.

import subprocess

'''
	Checking if the nginx process is running using the following command
	(and storing its output in a dict);
'''
(status, output) = subprocess.getstatusoutput('ps -A | grep nginx')

try:

	## Status = 0 if nginx is running and vice versa
	if status == 0:
		print('nginx is running: ' + output)

	else:
	    print('nginx is not running..')

	    ## Starting nginx
	    subprocess.run(['sudo', 'service', 'nginx', 'start'])
	    print('nginx is now running.')

except Exception as error:
	print('An error occured while trying to check if nginx was running: ' + error)