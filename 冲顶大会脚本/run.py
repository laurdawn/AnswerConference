# -*- coding: utf-8 -*-

import os, io, configparser, re
from PIL import Image
import getAnswer
from threading import Thread
import time, subprocess, webbrowser
import numpy as np
from aip import AipOcr
import urllib.parse

# 读取配置文件
config = configparser.ConfigParser()
config.read('./config/configure.conf', encoding='utf-8')
replace_reg = re.compile(r"[\s+\\!\/_,$%^*(+\"’“”《》<>\']+|[+——！，。？、~@#￥%……&*（）]+")

#获取手机截图
#返回Image类型
def getScreenShot():
	binary_screenshot = subprocess.check_output('adb shell screencap -p', shell=True).replace(b'\r\n', b'\n')
	return Image.open(io.BytesIO(binary_screenshot))

#抠图-题目
def getCddhTitle(img, type):
    combine_region = None
    if type == "1":
        combine_region = config.get("type", "CDDH")
    elif type == "2":
        combine_region = config.get("type", "BWYX")
    combine_region = list(map(int, combine_region.replace(' ','').split(',')))
    R, G, B = combine_region[0], combine_region[1], combine_region[2]
    img = img.convert("RGB")
    array = np.array(img)
    width, height = img.size
    left = None
    top = None
    right = None
    bottom = None
    #左坐标
    for i in range(width):
        r, g, b = array[height//2][i]
        if r == 255 and g == 255 and b == 255:
            left = i
            break
    #上坐标
    for i in range(height):
        r, g, b = array[i][width//2]
        if r == 255 and g == 255 and b == 255:
            top = i
            break
    #右坐标
    for i in range(width-1, 0 , -1):
        r, g, b = array[height//2][i]
        if r == 255 and g == 255 and b == 255:
            right = i
            break
    #下坐标
    for i in range(height-1, 0 , -1):
        r, g, b = array[i][width//2]
        if r == R and g == G and b == B:
            bottom = i
            break
    if left == None or top == None or right == None or bottom == None:
        return
    if type == "1":
    	left += 50
    	top += 260
    	bottom += 50
    elif type == "2":
    	#left += 40
    	top += 180
    	bottom += 50
    return img.crop((left, top, right, bottom))

#百度ocr识别
def ocr_img_baidu(img):
    APP_ID = config.get('baidu_api','APP_ID')
    API_KEY = config.get('baidu_api','API_KEY')
    SECRET_KEY = config.get('baidu_api','SECRET_KEY')
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    #return None, None
    #base64_data = base64.b64encode(region_im)
    response = client.basicGeneral(img_byte_arr.getvalue())
    #print(response)
    words_result = response['words_result']
    print("识别结果：", words_result)
    #print(words_result)
    texts = [x['words'] for x in words_result]
    # print(texts)
    question = texts[0]
    if "." in question:
        question = question.split(".")[1]
    choices = texts[1:]
    choices = [x.replace(' ', '') for x in choices]

    # 处理出现问题为两行或三行
    for i in range(len(choices)):
        if choices[i].endswith('?'):
            for j in range(i+1):
                question += choices[0]
                choices.pop(0)
            break
    for i in range(len(choices)):
        choices[i] = replace_reg.sub('', choices[i])
    if len(choices) < 1:
    	print("未识别到选项。。。")
    return question, choices

def main(type, operate):
	#测试图片
	#img = Image.open("./image/1516846977.png")
	if operate == "0":
		print("自动截图。。。")
		#自动抠图
		while True:
			img_start = time.clock()
			img = getScreenShot()
			if img == None:
				print("截图为空。。。")
				return
			img_title = getCddhTitle(img, type)
			img_end = time.clock()
			if img_title != None:
				#img_title.show()
				print("正在识别。。。")
				break
	elif operate == "1":
		print("手动截图。。。")
		#手动抠图
		img_start = time.clock()
		img = getScreenShot()
		if img == None:
			print("截图为空。。。")
			return
		img_title = getCddhTitle(img, type)
		img_end = time.clock()
		print("截图用时：", img_end-img_start)
		if img_title != None:
			img_title.show()
			print("正在识别。。。")
		else:
			print("抠图未识别到题目，请重试。。。")
			return
	else:
		print("未识别指令")
	start_ocr = time.clock()
    #ocr识别
	question, choices = ocr_img_baidu(img_title)
	end_ocr = time.clock()
	print('识别用时: {0}'.format(end_ocr - start_ocr))
	start_calculate = time.clock()
	webbrowser.open('https://baidu.com/s?wd=' + urllib.parse.quote(question))
	getAnswer.analyze(question, choices)
	end_calculate = time.clock()
	print('算法用时: {0}'.format(end_calculate - start_calculate))
	print('总计用时: {0}'.format(end_calculate - img_start))
	img.save("./image/" + str(int(time.time())) + ".png")


while True:
	type = input('请选择当前答题类型: ')
	if type == "1":
		print("您当前选择|冲顶大会|答题辅助。。。")
		break
	elif type == "2":
		print("您当前选择|百万英雄|答题辅助。。。")
		break
	elif type=="exit":
		print("退出脚本。。。")
		exit(0)
	else:
		print("暂不支持当前指令，等待开发。。。。")

while True:
	#不输入任何字符-截图测试
	#0-自动循环截图
	#1-手动截图
    go = input('请输入随机命令来查询结果: ')
    if go:
    	#try:
    	main(type, go)
    	#except Exception as e:
    	#	print("发生错误：", e)
    else:
    	start = time.clock()
    	img = getScreenShot()
    	img.save("./image/" + str(int(time.time())) + ".png")
    	end = time.clock()
    	print('截取测试图片用时: {0}'.format(end - start))

    print('-------------------------------命令执行完毕------------------------')