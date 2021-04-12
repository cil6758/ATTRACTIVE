#Developer: Yuan-Mao Hung
#Date: 2021/4/8
#Description: Parser.py parses the files
import dm

def Parse_title(s_file):	#Parse the training article titles.
	
	with open(s_file, "r") as fp:
		dict_article = {}
		for line in fp:
			sd_temp_article = dm.Article()
		
			l_ele = line.strip().split("\t")
			
			sd_temp_article.s_title = l_ele[0].strip('.')
			sd_temp_article.l_organ = l_ele[1].split(',')
			sd_temp_article.l_organ = [iter.strip('"') for iter in sd_temp_article.l_organ]
			sd_temp_article.l_animal = l_ele[2].split(',')
			sd_temp_article.l_animal = [iter.strip('"') for iter in sd_temp_article.l_animal]
			
			dict_article[sd_temp_article.s_title] = sd_temp_article
			
		print(len(dict_article))
			
		return dict_article
			
def Parse_abstract(s_file):	#Parse article abstracts
	
	with open(s_file, "r") as fp:
		dict_article = {}
		for line in fp:
			sd_temp_article = dm.Article()
		
			l_ele = line.strip().split("\t")
			
			sd_temp_article.s_title = l_ele[0].strip('.>')
			sd_temp_article.l_organ = l_ele[1].split(',')
			sd_temp_article.l_animal = l_ele[2].split(',')
			
			line = fp.readline()
			
			if(len(line.strip()) == 0):
				continue
			
			sd_temp_article.s_abstract = line.strip()
			
			dict_article[sd_temp_article.s_title] = sd_temp_article
			
		return dict_article
			
			