#Developer: Yuan-Mao Hung
#Date: 2021/4/8
#Description: autoupdate.py includes the methods to update the database automatically
import http.client	#for solving "IncompleteRead error"
import json
import os
import nltk
import pubmed_parser as pp
import re
import subprocess as sp
import sys
import time
import xml.etree.cElementTree as ET

from bs4 import BeautifulSoup
from joblib import load
from urllib import request
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer, LancasterStemmer
from urllib.request import urlopen
from website.models import Article

http.client.HTTPConnection._http_vsn = 10  #for solving "IncompleteRead error"
http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'	#for solving "IncompleteRead error"

l_stopwords = stopwords.words("english")
l_stopwords.append("via")

def Classify_by_cos_sim(dict_model, dict_obj):	#model_improved_tf_idf * obj_term_frequency		s_mode=train/validate
	
	obj_sum = 0
	for key,val in dict_obj.items():	#Calculate denominator for objective item(title or abstract)
		obj_sum += val**2
	
	import math
	
	obj_norm = math.sqrt(obj_sum)
	
	dict_organ_norm = {}
	
	for key,dict_tfidf in dict_model.items():
		n_organ_sum = 0
		
		for term,val in dict_tfidf.items():	#Calculate denominator for organ model
			n_organ_sum += val[2]**2
		
		f_organ_norm = math.sqrt(n_organ_sum)
		
		dict_organ_norm[key] = f_organ_norm
	
	dict_organ_score = {}	#dict_organ_score{organ:cos_sim_score}
	
	for organ,dict_tfidf in dict_model.items():
		
		f_dot_prod_sum = 0
		for term,val in dict_obj.items():
			if(term in dict_tfidf.keys()):
				f_dot_prod_sum += val * dict_tfidf[term][2]
				
		dict_organ_score[organ] = f_dot_prod_sum / (obj_norm * dict_organ_norm[organ])
	
	s_classify_organ = "unclassify"
	f_max_score = 0
	for key,val in dict_organ_score.items():
		if(val > f_max_score):
			s_classify_organ = key
			f_max_score = val
		
	if(f_max_score > 0):
		return s_classify_organ
	else:
		return "unclassify"

dict_search_target = {
	"pancreas" : [["pancreas"],["pancrea", "insulin", "islet"]],
	"kidney" : [["kidney", "renal", "nephron"],["kidney", "renal", "nephro"]],
	"epidermis" : [["epidermis"],["epiderm"]],
	"cornea" : [["keratocyte", "limbal", "corneal"],["keratocyt", "limbal", "cornea"]],
	"lung" : [["lung", "airway", "alveolar"],["lung", "airway", "alveolar"]],
	"muscle" : [["muscle", "myoblast", "myogen"],["muscle", "myoblast", "myogen"]],
	"schwann" : [["schwann"],["schwann"]],
	"dopaminergic" : [["dopaminergic"],["dopaminergic"]],
	"heart" : [["cardiac", "cardiomyocyte"],["heart", "cardi"]],
	"motor" : [["motor%20neuron"],["neuromuscular", "motoneuron", "motor neuron"]],
	"neuron" : [["neuron", "neural"],["neuro", "neural", "brain", "spinal cord", "neural crest"]],
	"mesoderm" : [["mesoderm"],["mesoderm"]],
	"endoderm" : [["endoerm"],["endoerm"]],
	"ectoderm" : [["ectoderm"],["ectoderm"]],
	"liver" : [["liver", "hepatocyte"],["liver", "hepatocyt"]],
	"osteoblast" : [["osteoblast", "osteogenesis", "osteocyte", "osteogenic"],["osteo"]],
	"chondrocyte" : [["chondrogenic", "chondrogenesis", "chondrocyte", "cartilage"],["chondro", "cartilage"]],
	"astrocyte" : [["astrocyte"],["astrocyt"]],
	"oligodendrocyte" : [["oligodendrocyte"],["oligodendrocyt"]],
	"reproductive" : [["oocyte", "germ", "ovarian"],["oocyt", "germ", "ovari"]],
	"retina" : [["retina", "photoreceptor"],["retina", "photoreceptor"]],
	"blood" : [["blood", "hematopoietic"],["blood", "hematopoiet"]],
	"endothelium" : [["endothelium", "vascular"],["endotheli", "vascular"]],
	"adipose" : [["adipocyte", "adipogenesis", "adipose"],["adipocyt", "adipogen", "adipos"]],
	"thyroid" : [["thyroid"],["thyroid"]],
	"melanocyte" : [["melanocyte"],["melanocyte"]]
}

l_keyTerm = ["pancrea", "insulin", "islet", "kidney", "renal", "nephro", "epiderm", "keratocyt", "limbal", "cornea", "lung", "airway", "alveolar", "muscle", "myoblast", "myogen", "schwann", "dopaminergic", "heart", "cardi", "neuromuscular", "motoneuron", "motor neuron", "neuro", "neural", "brain", "spinal cord", "neural crest", "mesoderm", "endoerm", "ectoderm", "liver", "hepatocyt", "osteo", "chondro", "cartilage", "astrocyt", "oligodendrocyt", "oocyt", "germ", "ovari", "retina", "photoreceptor" "blood", "hematopoiet", "endotheli", "vascular", "adipocyt", "adipogen", "adipos", "thyroid", "melanocyte"]
l_refuseWord = ["cancer", "carcinoma", "immun", "tumor", "polyp", "glioma", "glioblastoma", "leukemia", "leukemic", "leukemogenic", "mutation", "nk", "natural killer", "teratoma", "drosophila"]

s_rmdbPath = os.path.expanduser('~') + "your/path/to/project/"	#Set project path

for oIter,kwIter in dict_search_target.items():
	
	s_dir_keyword = oIter
	
	for kIter in kwIter[0]:
		s_key_word = kIter

		print("keyword: ", s_key_word, "\t", "organ: ", s_dir_keyword)

		if(not os.path.exists(s_rmdbPath + "organ_article/" + s_dir_keyword + "/")):	#Create article directory if not exist
			os.makedirs(s_rmdbPath + "organ_article/" + s_dir_keyword + "/")
		
		#Set usearch parameters
		s_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
		s_db = "pmc"
		s_query = s_key_word + "%20stem+cell+differentiation"
		s_esearch_retmode = "json"
		s_reldate = "200"
		s_datetype= "pdat"
		s_retmax = "100000"
		s_usehistory = "y"
		s_email = "d06945001@g.ntu.edu.tw"

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
				print(b_isGetIDList)
				
				break;
			except Exception as e:
				print(e)
				print("\nCan not connect to PMC database. Reconnect again...")
				b_isGetIDList = False
				n_fail_counter += 1

		l_PMCID = dict_PMID["esearchresult"]["idlist"]
		
		print("Search Article number: " + str(len(l_PMCID)))
		
		s_efetch_retmode = "xml"	#Set efetch parameters

		n_article_counter = 1

		headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}
	
		dict_checkedArticle = {}
		
		with open(s_rmdbPath + "RMDB/autoupdate/requested_article.txt", "r") as fp:	  
			for line in fp:
				if(line.strip() != "" and line.find("=") == -1):
					dict_checkedArticle[line.strip()] = 1
		
		print("Checked article number: " + str(len(dict_checkedArticle)))
		
		while(n_article_counter < len(l_PMCID)):
		
			for idIter in l_PMCID:
				if(idIter in dict_checkedArticle.keys()):
					print("\033[1;36;40mAlready checked the article: " + idIter + "\033[0m")
					n_article_counter += 1
					continue
				else:
					try:
						print("Checking Article " + str(n_article_counter) + ": " + idIter + "\t Progress: " + str(n_article_counter) + "/" + str(len(l_PMCID)) + "\t Category/Keyword: " + oIter + "/" + s_key_word )
					
						s_efetch_url = s_base + "efetch.fcgi?db=" + s_db + "&retmode=" +  s_efetch_retmode + "&id=" + idIter + "&tool=python" \
					   + "&email=" + s_email

						req = request.Request(url=s_efetch_url, headers=headers)
						response_article = urlopen(req, timeout=10)
					
						bs_article = BeautifulSoup(response_article.read(), "lxml")	#Get the article content in xml format
						
						s_article_title = " ".join(bs_article.find("article-title").get_text().strip().split())
						
						b_hasKeyword = False
						
						if(re.search(r"stem cell", s_article_title.lower()) != None and re.search(r"differentiat", s_article_title.lower()) != None):
							for kwIter in l_keyTerm:
								if(s_article_title.lower().find(kwIter) != -1):
									b_hasKeyword = True
									break
									
						
						b_hasRefuseWord = False
						l_title_word = s_article_title.lower().split(" ")
						for wIter in l_title_word:
							if(wIter in l_refuseWord):
								b_hasRefuseWord = True
								break
						
						
						if(b_hasKeyword == True and  b_hasRefuseWord == False):	#No need to include the key word since esearch will handle the key word seaerching job
							s_article_type = bs_article.find("subject").get_text().strip()
							if(s_article_type.lower() != "review"):
								bs_title_tag = bs_article.findAll("title")
								for tIter in bs_title_tag:
									s_title_content = tIter.text.strip().lower()
									
									if(len(s_title_content) < 40):
										if((re.search(r"material[s*] and method[s*]", s_title_content) != None or \
										   re.search(r"method[s*]", s_title_content) != None or \
										   re.search(r"protocol", s_title_content) != None or \
										   re.search(r"experimental", s_title_content) != None or \
										   re.search(r"procedure", s_title_content) != None) and \
										   re.search(r"statistical", s_title_content) == None): 
										   
											s_title = s_article_title
											
											s_author = bs_article.find("given-names").text.strip() + " " + bs_article.find("surname").text.strip() + " et. al."
											
											s_year = "-"
											
											bs_year = bs_article.find("pub-date", {"pub-type":"ppub"})
											if(bs_year == None):
												bs_year = bs_article.find("pub-date", {"pub-type":"epub"})
												if(bs_year == None):
													bs_year = bs_article.find("pub-date", {"pub-type":"collection"})
													if(bs_year == None):
														s_year = bs_article.find("year").text
														if(s_year == None):
															s_year = "-"
													else:
														s_year = bs_year.year.text
												else:
													s_year = bs_year.year.text
											else:
												s_year = bs_year.year.text
											
											s_journal = bs_article.find("journal-title").text
											if(s_journal.find('(') != -1):
												l_journal_name = s_journal.strip().split("(")
												s_journal = l_journal_name[0].strip()
											
											
											tokenizer = nltk.RegexpTokenizer(r"[a-zA-Z_]+")	#Remove punctuation and number
											l_word_tokens = tokenizer.tokenize(s_title)
											
											l_filter_term = []
											
											for iter in l_word_tokens:	#Remove stopwords
												if iter not in l_stopwords:
													l_filter_term.append(iter)
											
											nltk_stemmer = PorterStemmer()
											
											l_stem_term = []
											
											for iter in l_filter_term:
												l_stem_term.append(nltk_stemmer.stem(iter))	#stem all the title words
												
											dict_organ_model = load(s_rmdbPath + "RMDB/autoupdate/cos_model_abstract_lda_train_organ_static.joblib")
											
											dict_tf = {}
											
											for termIter in l_stem_term:
												if(termIter not in dict_tf.keys()):
													dict_tf[termIter] = 1
												else:
													dict_tf[termIter] += 1
											
											s_organ = Classify_by_cos_sim(dict_organ_model, dict_tf)
											
											if(s_organ != "unclassify"):
											
												if(s_organ.find("dopaminergic") != -1):
													s_organ = "dopaminergic neuron"
												elif(s_organ == "osteoblast"):
													s_organ = "bone"
												elif(s_organ == "chondrocyte"):
													s_organ = "cartilage"
												elif(s_organ == "motor"):
													s_organ = "motor neuron"
												elif(s_organ == "schwann"):
													s_organ = "schwann cell"
												elif(s_organ == "reproductive"):
													s_organ = "reproductive system"
												else:
													pass
												
												l_endoderm = ["liver", "lung", "pancreas", "thyroid"]
												l_mesoderm = ["adipose", "blood", "bone", "cartilage", "endothelium", "heart", "kidney", "reproductive system", "muscle"]
												l_ectoderm = ["neuron", "astrocyte", "dopaminergic neuron", "motor neuron", "oligodendrocyte", "epidermis", "cornea", "retina", "melanocyte", "schwann cell"]
												
												if(s_organ in l_endoderm):
													s_organ += ",endoderm"
												elif(s_organ in  l_mesoderm):
													s_organ += ",mesoderm"
												elif(s_organ in l_ectoderm):
													s_organ += ",ectoderm"
												
												s_date = time.strftime("%Y-%m-%d", time.localtime())
												
												s_link = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC" + idIter + "/"
												
												print("\033[1;32;40mCollect article: " + " ".join(s_article_title.strip().split()) + "\033[0m")
												print("\033[1;32;40mClassify organ: " + s_organ + "\033[0m")
												if(Article.objects.filter(s_article_id=idIter).exists() == False):
													Article.objects.create(s_article_id=idIter, s_title=s_title, s_author=s_author, n_year=int(s_year), s_journal=s_journal, s_organ=s_organ, s_link=s_link, s_col_date=s_date)
													with open(s_rmdbPath + "RMDB/autoupdate/store_db.tsv", "a") as fp:
														print("write to store_db.tsv")
														fp.write(s_title + "\t" + s_author + "\t" + s_year + "\t" + s_journal + "\t" + s_organ + "\t" + s_link + "\n")
												else:
													print("\033[1;33;40mArticle id " + idIter + " already exsists in the database.\033[0m")
							else:
								print("\033[1;33;40mThis is an review article. No download !\033[0m")
								pass
						
						else:
							print("\033[1;33;40mNot target article: " + " ".join(s_article_title.strip().split()) + "\033[0m")
							pass
						
						with open(s_rmdbPath + "RMDB/autoupdate/requested_article.txt", "a") as fp:
							fp.write(idIter + "\n")
						
						time.sleep(0.3)	#Set some time delay so that the pubmed server will not exceed its work load.
						
					except Exception as e:
						with open(s_rmdbPath + "RMDB/autoupdate/fail_dowload_id.txt", "a") as fp:
							fp.write("fail checked ID: " + idIter + "\n")
						
						with open(s_rmdbPath + "RMDB/autoupdate/fail_download_info.txt", "a") as fp:
							fp.write("fail checked ID: " + idIter + "\n")
							fp.write(str(e))
							fp.write("\n=================================================\n")
						
						print(e)
					
					n_article_counter += 1
