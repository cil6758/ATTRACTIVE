#Developer: Yuan-Mao Hung
#Date: 2021/4/8
#Description: Train.py includes the static model and cosine + LDA training algorithms
from joblib import dump, load

import Classify

import copy
import dm
import math

s_base = "/path/to/your/project/"	#Set your project path

def Train_cos_lda(dict_article, s_target):	#Training the static organ/tissue models and the LDA cosine models.
	
	dict_train_article = copy.deepcopy(dict_article)
	
	dict_organ_model = {}
	dict_organ_article_counter = {}	#calculate the belonging article number for each organ category -> dict_organ_article_counter{s_organ:n_number}
	
	f_alpha = 1
	
	dict_problem_article = {}
	
	n_osc_bound = 50
	
	if(s_target == "title"):
		for key,val in dict_train_article.items():	#Only for initilize
			s_organ = val.l_organ[0]
			
			if(s_organ not in dict_organ_article_counter.keys()):	#Build dict_organ_article_counter
				dict_organ_article_counter[s_organ] = 1
			else:
				dict_organ_article_counter[s_organ] += 1
			
			if(s_organ not in dict_organ_model.keys()):	#Build organ_model
				dict_organ_model[s_organ] = copy.deepcopy(val.dict_title_term)
			else:
				for tKey,tVal in val.dict_title_term.items():
					if(tKey in dict_organ_model[s_organ].keys()):
						for i in range(0,3):	#Sum the article vectors in the same categories.
							dict_organ_model[s_organ][tKey][i] += tVal[i]
					else:
						dict_organ_model[s_organ][tKey] = tVal
		
		for key,val in dict_organ_model.items():
			for tKey, tVal in val.items():
				for iter in tVal:
					iter = iter/dict_organ_article_counter[key]
		
		with open(s_base + "output/cos_model/cos_model_title_lda_ctfidf_train_organ.tsv", 'w', encoding = "utf-8") as wp:
			for key,val in dict_organ_model.items():
				wp.write("#" + key + "\n")
				for tKey,tVal in sorted(val.items()):
					wp.write(tKey + "\t" + str(tVal[2]) + "\n")
		
		dump(dict_organ_model, s_base + "output/cos_model/cos_model_title_lda_train_organ_static.joblib")
		

		b_isModelChange = False
		n_article_change_ID = None
		n_iteration_counter = 1
		
		#Starting to add LDA learning rule
		while(1):
			print("\033[1;33;40mIteration " + str(n_iteration_counter) + ":\033[0m")
			
			n_articleID_counter = 0
			
			for key,val in dict_article.items():
			
				s_organ = val.l_organ[0]
				s_classify_organ = Classify.Classify_cos_sim_improve(dict_organ_model, val.dict_title_term, "train")	#Classify the selected article
				if(s_classify_organ != val.l_organ[0]):	#If the classification result is not correct
					print("Modify model vector: " + s_organ + ", " + s_classify_organ)
					b_isModelChange = True	#Record whether any organ/tissue model has been changed.
					n_article_change_ID = n_articleID_counter
					for tKey,tVal in val.dict_title_term.items():
						if(tKey in dict_organ_model[s_organ].keys()):	#Increase the term weight of the correct class
							dict_organ_model[s_organ][tKey][2] += f_alpha * tVal[2]
						else:
							l_itf_idf_val = [0, 0, tVal[2]]
							dict_organ_model[s_organ][tKey] = l_itf_idf_val
						
						if(tKey in dict_organ_model[s_classify_organ].keys()):	#Decrease the term weight of the wrong class
							dict_organ_model[s_classify_organ][tKey][2] -= f_alpha * tVal[2]
						else:
							l_itf_idf_val = [0, 0, -tVal[2]]
							dict_organ_model[s_classify_organ][tKey] = l_itf_idf_val
					
					if(s_classify_organ not in val.dict_wrongOrgan_counter):
						val.dict_wrongOrgan_counter[s_classify_organ] = 1
					else:
						if(val.dict_wrongOrgan_counter[s_classify_organ] > n_osc_bound):
							dict_problem_article[key] = 1
							b_isModelChange = False
						else:
							val.dict_wrongOrgan_counter[s_classify_organ] += 1
							
				else:
					if(n_articleID_counter == n_article_change_ID):
						b_isModelChange = False
						break
					
				n_articleID_counter += 1
					
			s_outputPath = s_base + "output/cos_model/cos_model_title_lda_ctfidf_train_organ_v3.tsv"
			dump(dict_organ_model, s_base + "output/cos_model/cos_model_title_lda_train_organ_v3.joblib")
			
			with open(s_outputPath, 'w', encoding = "utf-8") as wp:
				for key,val in dict_organ_model.items():
					wp.write("#" + key + "\n")
					for tKey,tVal in sorted(val.items()):
						wp.write(tKey + "\t" + str(tVal[2]) + "\n")
						
			if(b_isModelChange == False):
				print("\033[1;33;40m" + "All the models have no change. Training complete!" + "\033[0m")
				break
				
			n_iteration_counter += 1
		
		with open(s_base + "output/cos_model/problem_article/problem_article_title.txt", 'w', encoding="utf-8") as wp:
			for key,val in dict_problem_article.items():
				wp.write(key + "\n")
		

	elif(s_target == "abstract"):
		for key,val in dict_train_article.items():	#Initilization
			s_organ = val.l_organ[0]
			
			if(s_organ not in dict_organ_article_counter.keys()):	#Build dict_organ_article_counter
				dict_organ_article_counter[s_organ] = 1
			else:
				dict_organ_article_counter[s_organ] += 1
			
			if(s_organ not in dict_organ_model.keys()):	#Build organ_model
				dict_organ_model[s_organ] = copy.deepcopy(val.dict_abstract_term)
			else:
				for tKey,tVal in val.dict_abstract_term.items():
					if(tKey in dict_organ_model[s_organ].keys()):
						for i in range(0,3):	#Sum the article vectors in the same category.
							dict_organ_model[s_organ][tKey][i] += tVal[i]
					else:
						dict_organ_model[s_organ][tKey] = tVal

		
		for key,val in dict_organ_model.items():
			for tKey, tVal in val.items():
				for iter in tVal:
					iter = iter/dict_organ_article_counter[key]
		
		with open(s_base + "output/cos_model/cos_model_abstract_lda_ctfidf_train_organ.tsv", 'w', encoding = "utf-8") as wp:
			for key,val in dict_organ_model.items():
				wp.write("#" + key + "\n")
				for tKey,tVal in sorted(val.items()):
					wp.write(tKey + "\t" + str(tVal[2]) + "\n")
		
		dump(dict_organ_model, s_base + "output/cos_model/cos_model_abstract_lda_train_organ_static.joblib")
				
		b_isModelChange = False
		n_article_change_ID = None
		n_iteration_counter = 1
		
		while(1):
			print("\033[1;33;40mIteration " + str(n_iteration_counter) + ":\033[0m")
			
			n_articleID_counter = 0
			
			for key,val in dict_article.items():
			
				s_organ = val.l_organ[0]
				s_classify_organ = Classify.Classify_cos_sim_improve(dict_organ_model, val.dict_abstract_term, "train")	#Classify the selected article
				if(s_classify_organ != val.l_organ[0]):
					print("Modify model vector: " + s_organ + ", " + s_classify_organ)
					b_isModelChange = True
					n_article_change_ID = n_articleID_counter
					for tKey,tVal in val.dict_abstract_term.items():
						if(tKey in dict_organ_model[s_organ].keys()):
							dict_organ_model[s_organ][tKey][2] += f_alpha * tVal[2]	#Increase the term weight of the correct class
						else:
							l_itf_idf_val = [0, 0, tVal[2]]
							dict_organ_model[s_organ][tKey] = l_itf_idf_val
						if(s_classify_organ != "unclassify"):	#"unclassify" class does not need to do any modification.
							if(tKey in dict_organ_model[s_classify_organ].keys()):
								dict_organ_model[s_classify_organ][tKey][2] -= f_alpha * tVal[2]	#Decrease the term weight of the wrong class	
							else:
								l_itf_idf_val = [0, 0, -tVal[2]]
								dict_organ_model[s_classify_organ][tKey] = l_itf_idf_val
								
					if(s_classify_organ not in val.dict_wrongOrgan_counter):
						val.dict_wrongOrgan_counter[s_classify_organ] = 1
					else:
						if(val.dict_wrongOrgan_counter[s_classify_organ] > n_osc_bound):
							dict_problem_article[key] = 1
							b_isModelChange = False
						else:
							val.dict_wrongOrgan_counter[s_classify_organ] += 1
								
				else:
					if(n_articleID_counter == n_article_change_ID):
						b_isModelChange = False
						break
					
				n_articleID_counter += 1
					
			s_outputPath = s_base + "output/cos_model/cos_model_abstract_lda_ctfidf_train_organ_v3.tsv"
			dump(dict_organ_model, s_base + "output/cos_model/cos_model_abstract_lda_train_organ_v3.joblib")
			
			with open(s_outputPath, 'w', encoding = "utf-8") as wp:
				for key,val in dict_organ_model.items():
					wp.write("#" + key + "\n")
					for tKey,tVal in sorted(val.items()):
						wp.write(tKey + "\t" + str(tVal[2]) + "\n")
						
			if(b_isModelChange == False):
				print("\033[1;33;40m" + "All the models have no change. Training complete!" + "\033[0m")
				break
				
			n_iteration_counter += 1
			
		with open(s_base + "output/cos_model/problem_article/problem_article_abstract.txt", 'w', encoding="utf-8") as wp:
			for key,val in dict_problem_article.items():
				wp.write(key + "\n")
		
	else:
		pass