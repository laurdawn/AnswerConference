#coding=utf8
from textrank4zh import TextRank4Keyword, TextRank4Sentence

text = "为防止小孩误食,任天堂特地在制作游戏机Switch的卡带上添加了什么"
tr4w = TextRank4Keyword()
tr4s = TextRank4Sentence()
tr4w.analyze(text=text, lower=True, window=2)
tr4s.analyze(text=text, lower=True, source = 'all_filters')

'''
def getkeywords():
	for item in tr4w.get_keywords(20, word_min_len=1):
		#if item.weight >= 0.1:
		print(item.word, item.weight)

def getkeyphrases():
	for item in tr4w.get_keywords(20, word_min_len=1):
		#if item.weight >= 0.1:
		print(item.word, item.weight)

def getkeysentences():
	for item in tr4s.get_key_sentences(num=3):
	    print(item.index, item.weight, item.sentence)  # index是语句在文本中位置，weight是权重

while True:
	go = input("请输入指令：")
	if go == "1":
		getkeywords()
	elif go == "2":
		getkeyphrases()
	elif go == '3':
		getkeysentences()
	else:
		print("不认识")
	print("--------------------我是指令结束分割线------------------")

'''
for s in tr4w.words_no_stop_words:
    print(s) 