#coding=utf8

from aip import AipNlp
import configparser

def similar(question, choices):
	config = configparser.ConfigParser()
	config.read('./config/configure.conf', encoding='utf-8')
	APP_ID = config.get('baidu_simnet','APP_ID')
	API_KEY = config.get('baidu_simnet','API_KEY')
	SECRET_KEY = config.get('baidu_simnet','SECRET_KEY')
	client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
	score = []
	options = {}
	options["model"] = "CNN"
	for i in range(len(choices)):
		score.append(client.simnet(question, choices[i], options)["score"])
	return score

if __name__ == '__main__':
	similar('5爱新觉罗玄烨是哪位清朝皇帝的名?', ['康熙', '雍正', '乾隆'])