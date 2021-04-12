#Developer: Yuan-Mao Hung
#Date: 2021/4/8
#Description: pub_parserTrain.py was used to organize the collected articles and extract their "title", "abstract", and " assigned organ/tissue" to a single file for the parser of the training algorithm.


from lxml import etree
import pubmed_parser as pp

import os
import re
import subprocess as sp


#The organ/tissue directories in the project
l_organ = ["adipose","astrocyte","blood","cartilage","cornea","dopaminergic","ectoderm","endoderm","endothelium", "epidermis","heart","kidney","liver","lung","melanocyte","mesoderm","motor","muscle","neuron","oligodendrocyte","osteoblast","pancreas","reproductive","retina","schwann","thyroid"]


s_rmdbPath = "Your/path/to/the/project"	#Set your path to the project

dict_article = {}	#dict_article = {article_ID: [title, abstract, organ]}
dict_exclude_article = {}	#dict_article = {article_ID: title}


for oIter in l_organ:
	print("Generate part: " + oIter)
	l_fileList = os.listdir(s_rmdbPath + "organ_article/" + oIter)

	for fIter in l_fileList:
		if(fIter.find(".xml") != -1):
			dict_article_feature = pp.parse_pubmed_xml(s_rmdbPath + "organ_article/" + oIter + "/" + fIter)
			
			s_title = " ".join(dict_article_feature["full_title"].strip().split())
			s_abstract = " ".join(dict_article_feature["abstract"].strip().split())
			
			if(len(s_abstract) == 0):
				continue
			
			s_category = ""
			
			if(fIter not in dict_exclude_article):
				if(fIter not in dict_article):
					l_element = [s_title, s_abstract, oIter, fIter]
					dict_article[fIter] = l_element
				else:
					dict_exclude_article[fIter] = s_title
					if(oIter.find("neuron") == -1):	#Since "motor neuron" and "dopaminergic neuron" includes neuron term, this will result in removing all the "motor neuron article". This statement is designed to prevent such kind of conflict.
						dict_article.pop(fIter)

for key,val in dict_article.items():
	with open(s_rmdbPath + "src/core/input/train_organ_title.tsv", "a+", encoding="utf-8") as wp:	#Generate the organized file for all the article titles.
		wp.write(val[0] + "\t" + val[2] + "\t" + "-" + "\t" + val[3] + "\n")
		
	with open(s_rmdbPath + "src/core/input/train_organ_abstract.tsv", "a+", encoding="utf-8") as wp:	#Generate the organized file for all the article abstracts.
		wp.write(">")
		wp.write(val[0] + "\t" + val[2] + "\t" + "-" + "\t" + val[3] + "\n")
		wp.write(val[1] + "\n")
