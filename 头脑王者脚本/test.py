#coding=utf8
import requests
data = requests.get(url='http://www.baidu.com/s', params={'wd': '铁观音属于哪种茶类？'}).text
p = data.find("mu=\"https://baike.baidu.com/item/")
startStr = "百度百科</a>"
endStr = "baike.baidu.com"
data = data[p:]
print(data)