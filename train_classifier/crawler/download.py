#Developer: Yuan-Mao Hung
#Date: 2021/4/8
#Description: download.py was used to collect the training articles

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib import request


import json
import os
import re
import subprocess as sp
import sys
import time
import xml.etree.cElementTree as ET


import http.client	#for solving "IincompleteRead error"
http.client.HTTPConnection._http_vsn = 10  #for solving "IincompleteRead error"
http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'	#for solving "IincompleteRead error"

dict_search_target = {
	"pancreas" : [["pancreas"],["pancrea", "insulin", "islet"]],	#finish: pancreas
	"kidney" : [["kidney", "renal", "nephron"],["kidney", "renal", "nephro"]],
	"epidermis" : [["epidermis"],["epiderm"]],
	"cornea" : [["keratocyte", "limbal", "cornea"],["keratocyt", "limbal", "cornea"]],
	"lung" : [["lung", "airway", "alveolar"],["lung", "airway", "alveolar"]],
	"muscle" : [["muscle"],["muscle", "myoblast", "myogen"]],
	"schwann" : [["schwann"],["schwann"]],
	"dopaminergic" : [["dopaminergic"],["dopaminergic"]],
	"heart" : [["cardiac", "cardiomyocyte"],["heart", "cardi"]],
	"motor" : [["motor%20neuron"],["neuromuscular", "motoneuron", "motor neuron"]],
	"neuron" : [["neuron", "neural"],["neuro", "neural"]],
	"mesoderm" : [["mesoderm"],["mesoderm"]],
	"endoderm" : [["endoerm"],["endoerm"]],
	"ectoderm" : [["ectoderm"],["ectoderm"]],
	"liver" : [["liver", "hepatocyte"],["liver", "hepatocyt"]],
	"osteoblast" : [["osteoblast", "osteogenesis", "osteocyte", "osteogenic"],["osteo"]],
	"chondrocyte" : [["chondrogenic", "chondrogenesis", "chondrocyte", "cartilage"],["chondro", "cartilage"]],
	"astrocyte" : [["astrocyte"],["astrocyt"]],
	"oligodendrocyte" : [["oligodendrocyte"],["oligodendrocyt"]],
	"reproductive" : [[["oocyte", "germ", "ovarian"]],["oocyt", "germ", "ovari"]],
	"retina" : [["retina", "photoreceptor"],["retina", "photoreceptor"]],
	"blood" : [["blood", "hematopoietic"],["blood", "hematopoiet"]],
	"endothelium" : [["endothelium", "vascular"],["endotheli", "vascular"]],
	"adipose" : [["adipocyte", "adipogenesis", "adipose"],["adipocyt", "adipogen", "adipos"]],
	"thyroid" : [["thyroid"],["thyroid"]],
	"melanocyte" : [["melanocyte"],["melanocyte"]]
}

s_rmdbPath = os.path.expanduser('~') + "Your/project/path/"	#Your project path

for oIter,kwIter in dict_search_target.items():

	s_dir_keyword = oIter
	
	for kIter in kwIter[0]:
		s_key_word = kIter

		print("keyword: ", s_key_word, "\t", "directory: ", s_dir_keyword)

		if(not os.path.exists(s_rmdbPath + "organ_article/" + s_dir_keyword + "/")):	#Create article directory if not exist
			os.makedirs(s_rmdbPath + "organ_article/" + s_dir_keyword + "/")
			#sp.run('mkdir ' + s_rmdbPath + s_dir_keyword + "/", shell=True)

		s_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"	#Set esearach parameter first
		s_db = "pmc"
		s_query = s_key_word + "%20stem+cell"
		s_esearch_retmode = "json"
		s_reldate = "7300"
		s_datetype= "pdat"
		s_retmax = "100000"
		s_usehistory = "y"
		s_email = "your_email"	#Set your e-mail
		
		#Form esearch url
		s_esearch_url = s_base + "esearch.fcgi?db=" + s_db + "&term=" + s_query + "&retmode=" + s_esearch_retmode + "&reldate=" \
		 + s_reldate + "&datetype=" + s_datetype + "&retmax=" + s_retmax + "&usehistory=" + s_usehistory + "&email=" + s_email 

		b_isGetIDList = False

		dict_PMID = {}

		n_fail_counter = 0

		if(n_fail_counter == 10):
			print("Failed to connect NCBI for 10 times. End the program")
			sys.exit(0)

		while(b_isGetIDList == False):
			try:
				html = urlopen(s_esearch_url, timeout=30)
				b_isGetIDList = True
				print("Start downloading article ID list from :" + s_esearch_url + " ...")
				bs = BeautifulSoup(html.read(), "html.parser")
				print("Finish downloading article ID list")
				print("=======================================================================")
				print("Start download article content...\n")
				
				dict_PMID = json.loads(str(bs))
				
				break;
			except Exception as e:
				print(e)
				print("\nCan not connect to PMC database. Reconnect again...")
				b_isGetIDList = False
				n_fail_counter += 1


		l_PMCID = dict_PMID["esearchresult"]["idlist"]	#Extract the response PMCID

		print("Searched Article number: " + str(len(l_PMCID)))
		

		s_efetch_retmode = "xml"

		n_article_counter = 1

		headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}

		dict_storedArticle = {}

		if(os.path.isfile(s_rmdbPath + "organ_article/" + oIter + "/" + "requested_article_" + oIter + ".txt") == False):
			f = open(s_rmdbPath + "organ_article/" + oIter + "/" + "requested_article_" + oIter + ".txt", "w+")
		else:
			with open(s_rmdbPath + "organ_article/" + oIter + "/" + "requested_article_" + oIter + ".txt", "r") as fp:	  
				for line in fp:
					if(line.strip() != ""):
						dict_storedArticle[line.strip()] = 1

		while(n_article_counter < len(l_PMCID)):
			for iter in l_PMCID:
				if(iter in dict_storedArticle.keys()):
					print("\033[1;36;40mAlready checked the article: " + iter + "\033[0m")
					n_article_counter += 1
					continue
				else:
					try:
						print("Download Article " + str(n_article_counter) + ": " + iter + "\t Progress: " + str(n_article_counter) + "/" + str(len(l_PMCID)) + "\t Category/Keyword: " + oIter + "/" + s_key_word )
						
						#Form efetch url
						s_efetch_url = s_base + "efetch.fcgi?db=" + s_db + "&retmode=" +  s_efetch_retmode + "&id=" + iter + "&tool=python" \
					   + "&email=" + s_email
						
						#Request the article content from PMC
						req = request.Request(url=s_efetch_url, headers=headers)
						response_article = urlopen(req, timeout=10)
					
						bs_article = BeautifulSoup(response_article.read(), "lxml")
						
						s_article_title = bs_article.find("article-title").get_text().strip()
						
						b_hasKeyword = False
						
						if(re.search(r"stem cell", s_article_title.lower()) != None):
							for ckIter in kwIter[1]:
								if(s_article_title.lower().find(ckIter) != -1):
									b_hasKeyword = True
									break
						
						if(b_hasKeyword == True and \
						(re.search(r"cancer", s_article_title.lower()) == None and \
						re.search(r"carcinoma", s_article_title.lower()) == None and \
						re.search(r"immun", s_article_title.lower()) == None and \
						re.search(r"tumor", s_article_title.lower()) == None)):	#The collection topics should not include cancer cells. 
							
							s_article_type = bs_article.find("subject").get_text().strip()
							if(s_article_type.lower() != "review"):	#Review article is not the type we need since review articles usually include many topics (organs/tissue) of regenerative medicine.
						
								print("\033[1;32;40mDownloaded article: " + " ".join(s_article_title.strip().split()) + "\033[0m")
								print("\033[1;32;40m===================================================================\033[0m")
								
								with open(s_rmdbPath + "organ_article/" + oIter + "/" + iter + ".xml", "w", encoding="utf-8") as fp:
									fp.write(bs_article.prettify())	#Output the article content
									
								if(os.path.isfile(s_rmdbPath + "organ_article/" + oIter + "/" + "downloaded_article.txt") == False):
									f = open(s_rmdbPath + "organ_article/" + oIter + "/" + "downloaded_article.txt", "w+")
									with open(s_rmdbPath + "organ_article/" + oIter + "/" + "downloaded_article.txt", "w", encoding="utf-8") as wp:
										wp.write(" ".join(s_article_title.strip().split()) + "\t" + iter + ".xml" + "\n")
								else:
									with open(s_rmdbPath + "organ_article/" + oIter + "/" + "downloaded_article.txt", "a", encoding="utf-8") as wp:
										wp.write(" ".join(s_article_title.strip().split()) + "\t" + iter + ".xml" + "\n")
									
							else:
								print("\033[1;33;40mThis is an review article. No download !\033[0m")
							
						else:
							print("\033[1;33;40mNot target article: " + " ".join(s_article_title.strip().split()) + "\033[0m")
							
						with open(s_rmdbPath + "organ_article/" + oIter + "/" + "requested_article_" + oIter + ".txt", "a") as fp:
							fp.write(iter + "\n")
						
						time.sleep(0.3)	#When using the crawler, remember to delay the program for some time so that the NCBI server will not be over loaded.
						n_article_counter += 1
						
					except Exception as e:
						with open(s_rmdbPath + "organ_article/" + oIter + "/" + "fail_dowload_id.txt", "a") as fp:
							fp.write("fail download ID: " + iter + "\n")
						
						with open(s_rmdbPath + "organ_article/" + oIter + "/" + "fail_download_info.txt", "a") as fp:
							fp.write("fail download ID: " + iter + "\n")
							fp.write(str(e))
							fp.write("\n=================================================\n")
						
						print(e)
						n_article_counter += 1

