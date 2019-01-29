#coding=utf8
import time
import json
import os
import connSql as conn
import requests
import webbrowser

# 读取问题与选项
def read_question():
    try:
        with open(r'./question.hortor.net/question/bat/findQuiz', encoding='utf-8') as f:
            response = json.load(f)
            question = response['data']['quiz']
            options = response['data']['options']
            # 搜索结果
            return quewry_db(question, options)
    except Exception as e:
        print("catch Exception:", e)
        time.sleep(0.5)
        read_question()

def quewry_db(question,choices):
    print("查询题库中...")
    index = conn.select(question,choices)
    if index != None:
        return index
    else:
        print("查询为空...")
        return count_base(question, choices)

def count_base(question,choices):
    print('词频计数法:')
    # 请求
    req = requests.get(url='http://www.baidu.com/s', params={'wd':question})
    content = req.text
    counts = []
    print('Question: ', question)
    print("choices:", choices)
    chosemore = True
    if '不是' in question:
        print('negative proposition, select least count...')
        chosemore = False
    for i in range(len(choices)):
        counts.append(content.count(choices[i]))
    return output(question, choices, counts, chosemore)


def output(question, choices, counts, more=True, type=1):
    counts = list(map(int, counts))
    # 计数最高
    index_max = counts.index(max(counts))
    # 计数最少
    index_min = counts.index(min(counts))
    if index_max == index_min:
        return
    if more:
        print("estimate answer is: ", choices[index_max])
        return index_max+1
    else:
        print("estimate answer is: ", choices[index_min])
        return index_min+1

if __name__ == '__main__':
	count_base('下列哪位京剧演员属于四大名旦？', "['张君秋', '荀慧生', '梅兰芳', '尚小云']")