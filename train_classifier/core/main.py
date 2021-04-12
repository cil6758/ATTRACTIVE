#Developer: Yuan-Mao Hung
#Date: 2021/4/8
#Description: main.py is the main function used to implement the algorithm
import Classify
import dm
import FileProcess
import Parser
import Train
import Validate

import time


s_base = "path/to/your/project/"

dict_article = {}

#===================================Train cosine model using LDA============================================

#Train title model
print("Parsing file...")
dict_article = Parser.Parse_title(s_base + "train_organ_title_v3.tsv")
print("File preprocessing...")
FileProcess.ProcessText(dict_article, "title")
print("Train cosine model based on LDA method")
Train.Train_cos_lda(dict_article, "title")	#Use LDA and cosine similarity to train model


#Train abstract model
print("Parsing file...")
dict_article = Parser.Parse_abstract(s_base + "train_organ_abstract_v3.tsv")
print("File preprocessing...")
FileProcess.ProcessText(dict_article, "abstract")
print("Train cosine model based on LDA method")
Train.Train_cos_lda(dict_article, "abstract")	#Use LDA and cosine similarity to train model


#====================================Validate collected articles using cosine similarity model=====================================

print("Classifying article based on title ...")
dict_article = Parser.Parse_title(s_base + "lifemap_title_v4.tsv")
dm.Check_training_article_num(dict_article)
FileProcess.ProcessText(dict_article, "title")
Classify.Validate_col_articles_organ_cos(dict_article, "title", "ctf_idf")


print("Classifying article based on abstract ...")
dict_article = Parser.Parse_abstract(s_base + "lifemap_abstract_v4.tsv")
FileProcess.ProcessText(dict_article, "abstract")
Classify.Validate_col_articles_organ_cos(dict_article, "abstract", "ctf_idf")


Classify.Measure_classification(dict_article, "abs-abs")

