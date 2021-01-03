#!/usr/bin/python3
from secrets import token_urlsafe
from os import getcwd
""
CWD = getcwd()
file_prefix = ""
if "server_files" in CWD:
	file_prefix = "../application/"
elif CWD == "application":
	file_prefix = ""

with open(file_prefix+'secret_key.txt','w') as fh:
	# This will generate log2(64**64) bits of randomness
	# or 384bits of total randomness. Could be raw bytes but I want to see it.
	# for now anyways.
	fh.write(token_urlsafe(64))

