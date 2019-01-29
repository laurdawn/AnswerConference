#coding=utf8
import random
import time, json
import os, sys
import getAnswer as answer
import connSql as conn
from watchdog.observers import Observer  
from watchdog.events import *

def run_adb_shell(stat):
	return os.popen(stat).read()

def clickScreen(param):
    if param == 1:
        run_adb_shell('adb shell input tap 500 900')
    elif param == 2:
        run_adb_shell('adb shell input tap 500 1100')
    elif param == 3 or param == 5:
        run_adb_shell('adb shell input tap 500 1300')
    elif param == 4:
        run_adb_shell('adb shell input tap 500 1500')
    elif param == 0:
        run_adb_shell('adb shell input tap 500 1700')


#获取尺寸
#print(run_adb_shell('adb shell wm size'))

#点击第一个选项(1)
#print(run_adb_shell('adb shell input tap 370 900'))

#点击第二个选项(2)
#print(run_adb_shell('adb shell input tap 370 1100'))

#点击第三个选项(3)/继续游戏(5)
#print(run_adb_shell('adb shell input tap 370 1300'))

#点击第四个选项(4)/智慧王者(0)
#print(run_adb_shell('adb shell input tap 370 1500'))

#获取截图
#print(run_adb_shell('adb shell screencap -p /sdcard/screenshop.png'))
#存截图到脚本目录下
#print(run_adb_shell('adb pull /sdcard/screenshop.png C:/Users/Administrator/Desktop/头脑王者脚本/img'))

def saveAnswer(info, answer):
    conn.insert()

#重写文件监控类
repeat = None
class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_modified(self, event):
        global repeat
        if event.is_directory:
            # 文件改变，读取题目内容json
            print("directory modified:{0}".format(event.src_path))
            #read_question()
        else:
            #print("file modified:{0}".format(event.src_path))
            if "match" in event.src_path:
                if repeat == "match":
                    return
                else:
                    repeat = "match"
                print("match is running, preparing...")
            elif "findQuiz" in event.src_path:
                if repeat == "findQuiz":
                    return
                else:
                    repeat = "findQuiz"
                print("read title, thinking...")
                time.sleep(4)
                try:
                    option = answer.read_question()
                except Exception as e:
                    print("catch Exception:", e)
                    print("rest 1s, retain title")
                    time.sleep(1)
                    option = answer.read_question()
                if option == None:
                    print("unknown answer,,,,,,")
                    option = random.randint(1,4)
                rest = random.randint(1,2)*random.random()
                #rest = random.random()
                print("imitate people thinking time", rest, "s")
                time.sleep(rest)
                print("现在点击答案", option)
                clickScreen(option)
            elif "choose" in event.src_path:
                if repeat == "choose":
                    return
                else:
                    repeat = "choose"
                print("answer is coming, save answer...")
                time.sleep(2)
                conn.insert()
            elif "fightResult" in event.src_path:
                if repeat == "fightResult":
                    return
                else:
                    repeat = "fightResult"
                print("match is over, prepare to next one。。。")
                time.sleep(5)
                clickScreen(5)
                time.sleep(3)
                clickScreen(0)

path = sys.path[0] + "/question.hortor.net/question/bat";
if __name__ == '__main__':
	event_handler = FileEventHandler()  
	observer = Observer()  
	observer.schedule(event_handler, path, recursive=True)  
	observer.start()  
	try:
	    while True:
	    	#print("休息1s...")
	    	time.sleep(1)
	except KeyboardInterrupt:
	    observer.stop()
	observer.join()