#Developer: Yuan-Mao Hung
#Date: 2021/4/8
#Description: change_encode.py was used to transform the collected code to the utf-8 encoding type so that the program could process the special characters.

import chardet
import os
import re
import subprocess as sp
import sys


print("\033[1;32;40m==============Modify encode================\n" + "\033[0m")

s_rmdbPath = "Your/path/to/the/project/"	#Set your path to the project


s_target_dir = "The_directory_name_you_used_to_store_the_collected_articles"	#Set the directory name you used to store your collected articles.

n_counter = 0
l_file = os.listdir(s_rmdbPath + s_target_dir)	#List the organ/tissue directories in the project

for fIter in l_file:
	print(fIter + ": \t" + str(n_counter) + "/" + str(len(l_file)))
	with open(s_rmdbPath + s_target_dir + "/" + fIter,'rb') as fp:
		encode_type = chardet.detect(fp.read())
		
		if(encode_type["encoding"] == "ascii" or encode_type["encoding"] == "utf-8"):
			pass
		else:
			print("convert encoding type from " + encode_type["encoding"] + " to utf-8: " + fIter)
			sp.run("iconv -t UTF-8 " + s_rmdbPath + s_target_dir + fIter + " -o " + s_rmdbPath + s_target_dir + "m_" + fIter, shell=True)	#Use iconv to transform the articles to utf-8 encoding.
	n_counter += 1	