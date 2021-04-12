class Article():	#Define article object.
	def __init__(self):
		self.s_title = ""
		self.s_abstract = ""
		self.s_content = ""
		self.l_keywords = []
		self.l_section = []
		
		self.l_organ = []
		self.l_animal = []
		
		self.dict_title_term = {}	#{feature_term: [tf, tf-idf, improved_tf-idf]}
		self.dict_abstract_term = {}
		self.dict_content_term = {}
		self.dict_section_term = {}
		self.dict_keyword_term = {}
		
		self.s_classify_organ = ""
		self.dict_wrongOrgan_counter = {}	#{"wrongOrgan":counter}	If wrong_organ_class > 50 -> abort this article
	
