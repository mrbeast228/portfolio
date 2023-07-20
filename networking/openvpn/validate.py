#!/usr/bin/env python3
from os import path
from hashlib import sha256
from sys import argv, exit

def hash(string):
	return sha256(string.encode('UTF-8')).hexdigest()

def userpass(user, passwd):
	return hash(user) + ':' + hash(passwd)

if argv[1] == 'createlogin':
	print(userpass(argv[2], argv[3]))
	exit(0)

upfile = open(path.dirname(path.abspath(__file__)) + '/.userpass', 'r')
uppairs = upfile.read().splitlines()
upfile.close()

logindatafile = open(argv[1], 'r')
login = logindatafile.read().splitlines()
logindatafile.close()

uppair = hash(login[0]) + ':' + hash(login[1])
exit(not uppair in uppairs)
