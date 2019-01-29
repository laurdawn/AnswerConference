#coding=utf8
import random
import time, json
import os, sys
import getAnswer
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

def saveAnswer(info, answer):
    conn.insert()

# 读取问题与选项
def read_question():
    try:
        with open(r'./question.hortor.net/question/bat/findQuiz', encoding='utf-8') as f:
            response = json.load(f)
            question = response['data']['quiz']
            options = response['data']['options']
            # 搜索结果
            return question, options
    except Exception as e:
        print("catch Exception:", e)
        time.sleep(0.5)
        read_question()

def quewry_db(question,choices):
    print("查询题库中...")
    index = conn.select(question,choices)
    return index

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
                question, choices = read_question()
                option = quewry_db(question,choices)
                if option == None:
                	print("题库为空...")
                	option = getAnswer.analyze(question, choices)
                #rest = random.uniform(0, 3)
                #rest = random.random()
                #print("imitate people thinking time", rest, "s")
                #time.sleep(rest)
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