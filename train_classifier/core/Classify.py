#Developer: Yuan-Mao Hung
#Date: 2021/4/8
#Description: Classify.py includes the validation and classification methods.
import copy
import dm
import math

from joblib import load

s_base = "path/to/your/project"

def Validate_col_articles_organ_cos(dict_article, s_target, s_metric):	#Parse model file and do classification for collected articles
	n_correct_num = 0
	
	if(s_target == "title"):
		dict_organ_model = load(s_base + "output/cos_model/cos_model_abstract_lda_train_organ_v3.joblib")
		if(s_metric == "ctf_idf"):
			for key,val in dict_article.items():
				val.s_classify_organ = Classify_cos_sim(dict_organ_model, val.dict_title_term, "validate", "ctf_idf")
				
				if(val.s_classify_organ in val.l_organ):
					n_correct_num += 1
				else:
					print(val.s_title + "\t" + val.s_classify_organ + "\t" + str(val.l_organ))
					
			
		elif(s_metric == "tf_idf"):
			for key,val in dict_article.items():
				val.s_classify_organ = Classify_cos_sim(dict_organ_model, val.dict_title_term, "validate", "tf_idf")
				
				if(val.s_classify_organ in val.l_organ):
					n_correct_num += 1
				else:
					print(val.s_title + "\t" + val.s_classify_organ + "\t" + str(val.l_organ))
					
		elif(s_metric == "tf"):
			for key,val in dict_article.items():
				val.s_classify_organ = Classify_cos_sim(dict_organ_model, val.dict_title_term, "validate", "tf")
				
				if(val.s_classify_organ in val.l_organ):
					n_correct_num += 1
				else:
					print(val.s_title + "\t" + val.s_classify_organ + "\t" + str(val.l_organ))
	elif(s_target == "abstract"):
		dict_organ_model = load(s_base + "output/cos_model/cos_model_abstract_lda_train_organ_v3.joblib")
		if(s_metric == "ctf_idf"):
			for key,val in dict_article.items():
				val.s_classify_organ = Classify_cos_sim(dict_organ_model, val.dict_abstract_term, "validate", "ctf_idf")
				
				if(val.s_classify_organ in val.l_organ):
					n_correct_num += 1
				else:
					print(val.s_title + "\t" + val.s_classify_organ + "\t" + str(val.l_organ))
		elif(s_metric == "tf_idf"):
			for key,val in dict_article.items():
				val.s_classify_organ = Classify_cos_sim(dict_organ_model, val.dict_abstract_term, "validate", "tf_idf")
				
				if(val.s_classify_organ in val.l_organ):
					n_correct_num += 1
				else:
					print(val.s_title + "\t" + val.s_classify_organ + "\t" + str(val.l_organ))
		elif(s_metric == "tf"):
			for key,val in dict_article.items():
				val.s_classify_organ = Classify_cos_sim(dict_organ_model, val.dict_abstract_term, "validate", "tf")
				
				if(val.s_classify_organ in val.l_organ):
					n_correct_num += 1
				else:
					print(val.s_title + "\t" + val.s_classify_organ + "\t" + str(val.l_organ))
	else:
		pass
		
	print("Accuracy(" + str(n_correct_num) + "/" + str(len(dict_article)) + ") = " + str(float(n_correct_num/len(dict_article))))

#Classify based on cosine similariy	
def Classify_cos_sim(dict_model, dict_obj, s_mode, s_featureMode):	#model_ctf_idf * obj_term_frequency		s_mode=train/validate	s_featureMode="tf","tfidf","ctfidf"
	
	obj_sum = 0
	for key,val in dict_obj.items():
		obj_sum += val[0]**2
	
	obj_norm = math.sqrt(obj_sum)
	
	dict_organ_norm = {}
	
	for key,dict_tfidf in dict_model.items():
		n_organ_sum = 0
		
		for term,val in dict_tfidf.items():
			if(s_featureMode == "ctf_idf"):
				n_organ_sum += val[2]**2
			elif(s_featureMode == "tf_idf"):
				n_organ_sum += val[1]**2
			elif(s_featureMode == "tf"):
				n_organ_sum += val[0]**2
			else:
				print("Unknown feature mode, apply ctf-idf:")
				n_organ_sum += val[2]**2
		
		f_organ_norm = math.sqrt(n_organ_sum)
		
		dict_organ_norm[key] = f_organ_norm
	
	dict_organ_score = {}	#dict_organ_score{organ:cos_sim_score}
	
	for organ,dict_tfidf in dict_model.items():
		
		f_dot_prod_sum = 0
		for term,val in dict_obj.items():
			if(term in dict_tfidf.keys()):
				if(s_featureMode == "ctf_idf"):
					f_dot_prod_sum += val[0] * dict_tfidf[term][2]
				elif(s_featureMode == "tf_idf"):
					f_dot_prod_sum += val[0] * dict_tfidf[term][1]
				elif(s_featureMode == "tf"):
					f_dot_prod_sum += val[0] * dict_tfidf[term][0]
				else:
					f_dot_prod_sum += val[0] * dict_tfidf[term][2]
				
		dict_organ_score[organ] = f_dot_prod_sum / (obj_norm * dict_organ_norm[organ])
		
	
	s_classify_organ = "unclassify"
	f_max_score = 0
	for key,val in dict_organ_score.items():
		if(val > f_max_score):
			s_classify_organ = key
			f_max_score = val

		
		
	if(s_mode == "train"):	#train mode
		return s_classify_organ
	
	else:	#validation mode
		if(f_max_score > 0):
			return s_classify_organ
		else:
			return "unclassify"
			