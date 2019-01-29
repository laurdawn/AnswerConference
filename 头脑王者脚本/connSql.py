#coding=utf8
import re
import pymysql.cursors
import json, datetime

config = {
          'host':'127.0.0.1',
          'port':3306,
          'user':'root',
          'password':'laurdawn',
          'db':'brain_king',
          'charset':'utf8',
          'cursorclass':pymysql.cursors.DictCursor,
          }
insertSql = 'INSERT INTO collection (num, quiz, options, answer, school, type, result, curTime, endTime, createDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
selectSql = 'select * from collection where quiz = %s'
conn = pymysql.connect(**config)

def read_question():
    with open(r'./question.hortor.net/question/bat/findQuiz', encoding='utf-8') as f:
        response = json.load(f)
        return response['data']

def read_answer():
    with open(r'./question.hortor.net/question/bat/choose', encoding='utf-8') as f:
        response = json.load(f)
        return response['data']

def getConn():
  global conn
  if conn.open:
    return
  else:
    conn = pymysql.connect(**config)
def insert():
  try:
    getConn()
    with conn.cursor() as cursor:
      # 执行sql语句，插入记录
        info = read_question()
        #print(info)
        answer = read_answer()
        #print("answer:", answer)
        if answer['answer'] == answer['option']:
          result = 1
          print("答案正确")
        else:
          result = 0
          print("答案错误，正确答案为:", answer['answer'])
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S');
        cursor.execute(insertSql, (int(info['num']), str(info['quiz']), str(info['options']), int(answer['answer']), str(info['school']), 
          str(info['type']), result, str(info['curTime']), str(info['endTime']), now));
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
    conn.commit()
  except Exception as e:
    print("catch Exception:", e)
    return

def select(question,choices):
  try:
    getConn()
    with conn.cursor() as cursor:
      cursor.execute(selectSql, question)
      row = cursor.fetchone()
      if row == None:
        return
      if row['quiz'] == question:
        index = int(row['answer'])
        print(row)
        option = str(row['options']).replace("\'", '').replace('[', '').replace(']', '').replace(' ', '').split(',')[index-1]
        print(option)
        choices = str(choices).replace("\'", '').replace('[', '').replace(']', '').replace(' ', '').split(',')
        for i in range(len(choices)):
          if option == choices[i]:
            return i+1
    conn.commit()
  except Exception as e:
    print("catch Exception:", e)
    return

if __name__ == '__main__':
  print(select('世界上海拔最高的淡水湖是？', "['苏必利尔湖', '玛旁雍错', '贝加尔湖', '马瑟森湖']"))