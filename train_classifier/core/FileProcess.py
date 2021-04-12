#Developer: Yuan-Mao Hung
#Date: 2021/4/8
#Description: FileProcess.py includes all the file preprocessing functions
import copy
import dm
import math
import nltk

from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer, LancasterStemmer

s_base = "path/to/your/project/"	#Set your project path

l_stopwords = stopwords.words("english")
l_stopwords.append("via")

def Case_fold(sd_inst):	#Transform all the parsed words to lower case.
	if(isinstance(sd_inst, str) == True):	
		return sd_inst.lower()
	elif(isinstance(sd_inst, list) == True):	
		return [x.lower() for x in sd_inst]
	else:
		print("Unaccepted type for case folding: " + sd_inst)
		
def Filter(sd_inst):	#Remove stopwords and punctuation

	if(isinstance(sd_inst, str) == True):	#input is a string
		tokenizer = nltk.RegexpTokenizer(r"[a-zA-Z_]+")	#Remove punctuation and number
		l_word_tokens = tokenizer.tokenize(sd_inst)
		
		l_filter_term = []
		
		for iter in l_word_tokens:	#Remove stopwords
			if iter not in l_stopwords:
				l_filter_term.append(iter)
		
		return l_filter_term
		
	elif(isinstance(sd_inst, list) == True):	#input is a list
		pass
	else:
		print("Unaccepted type for Filtering: " + sd_inst)
		
def Stem(l_filter_term, s_stemmer_type):	#stemmer type:  "porter"->PorterStemmer, "lancaster"->LancasterStemmer

	nltk_stemmer = None

	if(s_stemmer_type == "porter"):	#Apply PorterStemmer
		nltk_stemmer = PorterStemmer()	
	elif(s_stemmer_type == "lancaster"):	#Apply LancasterStemmer
		nltk_stemmer = LancasterStemmer()
		
	l_stem_term = []
	
	for iter in l_filter_term:
		l_stem_term.append(nltk_stemmer.stem(iter))
	
	return l_stem_term
	
	
def Calc_tf(l_term):	#Calculate term frequency
	
	dict_tf = {}
	
	n_term_sum = 0
	
	for iter in l_term:
		if iter not in dict_tf.keys():
			dict_tf[iter] = 1
		else:
			dict_tf[iter] += 1
			
		n_term_sum += 1
	
	for iter in dict_tf:
		dict_tf[iter] = dict_tf[iter] / n_term_sum
			
	return dict_tf
	
def Calc_tf_idf(dict_article, s_target):	#Calculate term frequency-inverse document frequency
	dict_term_df = {}	#document frequency of terms
	
	if(s_target == "title"):
	
		for key, val in dict_article.items():
			for iter in val.dict_title_term.keys():
				if(iter not in dict_term_df.keys()):
					dict_term_df[iter] = 0
		
		print("calculcate dict_term_df")
		for iter in dict_term_df:
			for key,val in dict_article.items():
				if(iter in val.dict_title_term.keys()):
					dict_term_df[iter] += 1
		
		print("calculate idf")
		
		for key,val in dict_article.items():
			for tKey, fVal in val.dict_title_term.items():
				idf = math.log(len(dict_article)/dict_term_df[tKey])
				tf = fVal[0]
				fVal.append(tf * idf)
				
	elif(s_target == "abstract"):
		for key, val in dict_article.items():
			for iter in val.dict_abstract_term.keys():
				if(iter not in dict_term_df.keys()):
					dict_term_df[iter] = 0
		
		print("calculcate dict_term_df")
		for iter in dict_term_df:
			for key,val in dict_article.items():
				if(iter in val.dict_abstract_term.keys()):
					dict_term_df[iter] += 1
		
		print("calculate idf")
		
		for key,val in dict_article.items():
			for tKey, fVal in val.dict_abstract_term.items():
				idf = math.log(len(dict_article)/dict_term_df[tKey])
				tf = fVal[0]
				fVal.append(tf * idf)
				
		
def Calc_improved_tf_idf(dict_article, s_target):
	dict_organ_model = {}	#{organ_tissue: dict_tfidf{term:[tf, tf_idf value]}}
	dict_organ_counter = {}
	
	if(s_target == "title"):
		dict_copy_article = copy.deepcopy(dict_article)	#deep copy should copy the full instance
		print("Build organ model...")
		for key,val in dict_copy_article.items():
			for oIter in val.l_organ:
				if(oIter not in dict_organ_model.keys()):
					dict_organ_model[oIter] = copy.deepcopy(val.dict_title_term)
					dict_organ_counter[oIter] = 1
				else:
					dict_organ_counter[oIter] += 1
					for tKey, tVal in val.dict_title_term.items():
						if(tKey in dict_organ_model[oIter].keys()):
							dict_organ_model[oIter][tKey][0] += tVal[0]
							dict_organ_model[oIter][tKey][1] += tVal[1]
						else:
							dict_organ_model[oIter][tKey] = tVal
							
		print("Build term class frequency dictionary...")
		dict_term_class_freq = {}	#dict_term_class_freq={term:class_appear_frequency}
		for key,val in dict_organ_model.items():
			for tKey,tVal in val.items():
				if(tKey not in dict_term_class_freq.keys()):
					dict_term_class_freq[tKey] = 1
				else:
					dict_term_class_freq[tKey] += 1
		
		print("Calculate improved tf-idf...")
		
		for key,val in dict_article.items():
			for tKey,fVal in val.dict_title_term.items():
				if(tKey in dict_term_class_freq):
					f_improved_param = math.log(len(dict_organ_model)/dict_term_class_freq[tKey])
					fVal.append(fVal[1] * f_improved_param)
				
	elif(s_target == "abstract"):
		dict_copy_article = copy.deepcopy(dict_article)	#deep copy should copy the full instance
		print("Build organ model...")
		for key,val in dict_copy_article.items():
			for oIter in val.l_organ:
				if(oIter not in dict_organ_model.keys()):
					dict_organ_model[oIter] = copy.deepcopy(val.dict_abstract_term)
					dict_organ_counter[oIter] = 1
				else:
					dict_organ_counter[oIter] += 1
					for tKey, tVal in val.dict_abstract_term.items():
						if(tKey in dict_organ_model[oIter].keys()):
							dict_organ_model[oIter][tKey][0] += tVal[0]
							dict_organ_model[oIter][tKey][1] += tVal[1]
						else:
							dict_organ_model[oIter][tKey] = tVal
							
		print("Build term class frequency dictionary...")
		dict_term_class_freq = {}	#dict_term_class_freq={term:class_appear_frequency}
		for key,val in dict_organ_model.items():
			for tKey,tVal in val.items():
				if(tKey not in dict_term_class_freq.keys()):
					dict_term_class_freq[tKey] = 1
				else:
					dict_term_class_freq[tKey] += 1
		
		print("Calculate improved tf-idf...")
		
		for key,val in dict_article.items():
			for tKey,fVal in val.dict_abstract_term.items():
				if(tKey in dict_term_class_freq):
					f_improved_param = math.log(len(dict_organ_model)/dict_term_class_freq[tKey])
					fVal.append(fVal[1] * f_improved_param)
	
def OutputOrganKeywords(dict_article, s_target):	#Output organ keywords based on improved tf-idf(Default: the first 10 keywords)
	dict_organ_model = {}	#{organ_tissue: dict_tfidf{term:tf_idf value}}

	if(s_target == "title"):
		for key,val in dict_article.items():
			for oIter in val.l_organ:
				if(oIter not in dict_organ_model.keys()):
					dict_organ_model[oIter] = copy.deepcopy(val.dict_title_term)
				else:
					for tKey, tVal in val.dict_title_term.items():
						if(tKey in dict_organ_model[oIter].keys()):
							dict_organ_model[oIter][tKey][0] += tVal[0]
							dict_organ_model[oIter][tKey][1] += tVal[1]
						else:
							dict_organ_model[oIter][tKey] = tVal
							
		with open(s_base + "output/organ_keywords/" + s_target + "_organ_keyword.tsv", 'w', encoding = "utf-8") as wp:
			for key,val in dict_organ_model.items():
				wp.write("#" + key + "\n")
				
				dict_sorted_keyword = sorted(val.items(), key=lambda x: x[1][2], reverse=True)
				
				for tKey,tVal in dict_sorted_keyword:
					wp.write(tKey + "\t" + str(tVal[2]) + "\n")
							
	elif(s_target == "abstract"):
		for key,val in dict_article.items():
			for oIter in val.l_organ:
				if(oIter not in dict_organ_model.keys()):
					dict_organ_model[oIter] = copy.deepcopy(val.dict_abstract_term)
				else:
					for tKey, tVal in val.dict_abstract_term.items():
						if(tKey in dict_organ_model[oIter].keys()):
							dict_organ_model[oIter][tKey][0] += tVal[0]
							dict_organ_model[oIter][tKey][1] += tVal[1]
						else:
							dict_organ_model[oIter][tKey] = tVal
							
		with open(s_base + "output/organ_keywords/" + s_target + "_organ_keyword.tsv", 'w', encoding = "utf-8") as wp:
			for key,val in dict_organ_model.items():
				wp.write("#" + key + "\n")
				
				dict_sorted_keyword = sorted(val.items(), key=lambda x: x[1][2], reverse=True)
				
				for tKey,tVal in dict_sorted_keyword:
					wp.write(tKey + "\t" + str(tVal[2]) + "\n")

	
def ProcessText(dict_article, s_target):	#File preprocessing for the subsequent text-mining

	l_filter_term = []
	l_stem_term = []

	if(s_target == "title"):
		for key,val in dict_article.items():
			val.s_title = Case_fold(val.s_title)	#Case folding
			l_filter_term = Filter(val.s_title)	#Remove stop words
			
			l_stem_term = Stem(l_filter_term, "porter")	#Porter stem
			dict_tf = Calc_tf(l_stem_term)	#Calculate TF value for each article
			
			for iter in dict_tf:
				l_tf = [dict_tf[iter]]
				val.dict_title_term[iter] = l_tf

		Calc_tf_idf(dict_article, "title")	#Calculate TF-IDF value for each article
		
		print("TF-IDF calculation is complete")
		
		Calc_improved_tf_idf(dict_article, "title")
		
		print("CTF-IDF calculation is complete")
			
	elif(s_target == "abstract"):
		for key,val in dict_article.items():
			val.s_abstract = Case_fold(val.s_abstract)	#Case folding
			l_filter_term = Filter(val.s_abstract)	#Remove stop words
			
			l_stem_term = Stem(l_filter_term, "porter")	#Porter stem
			
			dict_tf = Calc_tf(l_stem_term)
			
			for iter in dict_tf:
				l_tf = [dict_tf[iter]]
				val.dict_abstract_term[iter] = l_tf

		Calc_tf_idf(dict_article, "abstract")
		
		print("TF-IDF calculation is complete.")
		
		Calc_improved_tf_idf(dict_article, "abstract")
		
		print("CTF-IDF calculation is complete")
	else:
		pass
		