#coding=utf8
import requests
from concurrent.futures import ThreadPoolExecutor
# # 颜色兼容Win 10
from colorama import init,Fore
init()

Str_BeforeItem = open("./Str_BeforeItem.txt", 'r').read()
problemData = None
problemCnt = 0
deny = True
baiDuZhiDaoAnswerIndex = 0
zdRatio = 0
def analyze(question,choices):
    global deny
    print("Question:{}".format(question))
    print("Choices:{}".format(choices))
    question = removeUnuseInfo(question)
    open_baidu_count(question, 0)
    executor = ThreadPoolExecutor(len(choices)*3)
    #选项计数
    type = []
    for i in range(len(choices)):
        type.append(1)
    answerCnt = list(executor.map(open_baidu_count, choices, type))
    question_and_choices = list(map(lambda x: question + ' ' + x, choices))
    #选项+题目计数
    problemAndAnswerCnt = list(executor.map(open_baidu_count, question_and_choices, type))
    #词频计数
    rateCnt = list(executor.map(count_base, choices))
    pmiRank = CalculatePMIRank(problemCnt, answerCnt, problemAndAnswerCnt)
    cntRank = CalculateCountRank(question, rateCnt, pmiRank)
    sumRank = {}
    for i in range(len(choices)):
        sumRank[choices[i]] = 0
    pmiAddCnt = 0
    for i in range(len(choices)):
        pmiAddCnt += pmiRank[i] + cntRank[i]
    trueAnswerIndex = SearchTureAnswer(problemData, choices)
    if trueAnswerIndex != -1:
        sumRank[choices[trueAnswerIndex]] = pmiAddCnt
    else:
        if SearchInBaiduZhiDao(problemData, choices):
            sumRank[choices[baiDuZhiDaoAnswerIndex]] += pmiAddCnt * zdRatio / 100
            print("百度知道答案:", baiDuZhiDaoAnswerIndex, " Ratio:", zdRatio)
    maxIndex = 0
    minIndex = 0
    for i in range(len(choices)):
        sumRank[choices[i]] += pmiRank[i] + cntRank[i]
        if sumRank[choices[i]] > sumRank[choices[maxIndex]]:
            maxIndex = i
        if sumRank[choices[i]] < sumRank[choices[minIndex]]:
            minIndex = i
    #region 计算概率
    probabilitySum = 0
    for i in range(len(cntRank)):
        probabilitySum += sumRank[choices[i]]
    probability = []
    for i in range(len(choices)):
        probability.append(round(sumRank[choices[i]] / probabilitySum * 100, 2))
    #根据当前统计确定答案index
    if not deny:
        #print("否定语句，选择最少的")
        answer = minIndex + 1
    else:
        answer = maxIndex + 1
    print(Fore.YELLOW + "-----------------------------统计结果----------------------------" + Fore.RESET)
    #显示词频结果
    print("词频结果：")
    index_max = rateCnt.index(max(rateCnt))
    index_min = rateCnt.index(min(rateCnt))
    if index_max == index_min:
        print(Fore.RED + "高低计数相等此方法失效！" + Fore.RESET)
    else:
        for i in range(len(rateCnt)):
            if i == index_max:
                # 绿色为计数最高的答案
                print(Fore.GREEN + "{} : {}次".format(choices[i], rateCnt[i]) + Fore.RESET)
            elif i == index_min:
                # 红色为计数最低的答案
                print(Fore.MAGENTA + "{} : {}次".format(choices[i], rateCnt[i]) + Fore.RESET)
            else:
                print("{} : {}次".format(choices[i], rateCnt[i]))
        if deny and sum(rateCnt)-max(rateCnt) <= max(rateCnt):
            print("特征突出，推荐当前答案：{}".format(choices[rateCnt.index(max(rateCnt))]))
            answer = rateCnt.index(max(rateCnt)) + 1
    print()
    #统计概率结果
    print("统计概率结果：")
    for i in range(len(probability)):
        if i == maxIndex:
            # 绿色为计数最高的答案
            print(Fore.GREEN + "{} : {}%".format(choices[i], probability[i]) + Fore.RESET)
        elif i == minIndex:
            # 红色为计数最低的答案
            print(Fore.MAGENTA + "{} : {}%".format(choices[i], probability[i]) + Fore.RESET)
        else:
            print("{} : {}%".format(choices[i], probability[i]))
    print(Fore.YELLOW + "-----------------------------统计结束----------------------------" + Fore.RESET)
    deny = True
    return answer

def CalculatePMIRank(problemCnt, answerCnt, problemAndAnswerCnt):
    pmiRank = []
    for i in range(len(answerCnt)):
        pmiRank.append(int(problemAndAnswerCnt[i]) * int(problemAndAnswerCnt[i]) / int(problemCnt) / int(answerCnt[i]))
    return pmiRank

def CalculateCountRank(question, rateCnt, pmiRank):
    pmiSum = sum(pmiRank)
    sumCnt = sum(rateCnt)
    countRank = []
    if sumCnt == 0:
        sumCnt = 1
    for i in range(len(rateCnt)):
        countRank.append(pmiSum * (rateCnt[i] / sumCnt))
    return countRank

def removeUnuseInfo(question):
    global deny
    if "不是" in question or  "不属于" in question or  "不包括" in question or "不存在" in question or "不能" in question or "不在" in question or "不含" in question or  "不可以" in question or  "不包" in question or  "不需要" in question or  "错误" in question or  "没有" in question or  "不会" in question or  "不可能" in question or  "找不到" in question :
        print("否定语句，选择最少的")
        deny = False
    return question.replace("不是", "是").replace("不存在", "存在").replace("不能", "能").replace("不在", "在").replace("不含", "含").replace("不属于", "属于").replace("不可以", "可以").replace("不包", "包").replace("不需要", "需要").replace("错误", "正确").replace("没有", "有").replace("不会", "会").replace("不可能", "可能").replace("找不到", "能找到")


def count_base(str):
    counts = problemData.count(str)
    return counts

def open_baidu_count(str, type = 1):
    global problemData, problemCnt
    req = requests.get(url='http://www.baidu.com/s', params={'wd': str})
    content = req.text
    index = content.find('百度为您找到相关结果约') + 11
    content = content[index:]
    index = content.find('个')
    #返回百度计数
    count =  content[:index].replace(',', '')
    if count == "0":
        count = '1'
    if type == 0:
        problemData = content
        problemCnt = count
        return
    return count

def open_google_count(str, type = 1):
    global problemData, problemCnt
    req = requests.get(url='https://www.google.com.tr/search', params={'q': str})
    content = req.text
    index = content.find('搜狗已为您找到约') + len('搜狗已为您找到约')
    content = content[index:]
    index = content.find('条')
    #返回百度计数
    count =  content[:index].replace(',', '')
    if count == "0":
        count = '1'
    if type == 0:
        problemData = content
        problemCnt = count
        return
    return count

def SearchTureAnswer(data, answerArr):
    #百度计算器
    p = data.find("mu=\"http://open.baidu.com/static/calculator/calculator.html\"")
    if p != -1 :
        #确保词条在前两项
        if CountItemsBeforeP(data, p) < 2:
            p = data.find("<p class=\"op_new_val_screen_result\">", p)
            if p != -1:
                startP = data.find("<span>", p)
                if startP != -1 :
                    endP = data.find("</span>", startP)
                    if endP != -1:
                        ans = data[startP + len("<span>"):endP]
                        ans = ans.replace(" ", "")
                        #正确答案存在个数
                        existCnt = 0
                        #正确答案下标
                        index = 0
                        for i in range(len(answerArr)):
                            if answerArr[i] in ans:
                                existCnt += 1
                                index = i
                        if existCnt == 1 :
                            print("匹配到百度计算器:{}".format(answerArr[index]))
                            return index
    #百度汉语
    p = data.find("<div class=\"op_exactqa_detail_s_answer\">")
    if p != -1 :
        #确保词条在前两项
        if CountItemsBeforeP(data, p) < 2:
            startStr = "target=\"_blank\">"
            endStr = "</a></span>"

            startP = data.find(startStr, p)
            if startP != -1 :
                endP = data.find(endStr, startP)
                if endP != -1:
                    ans = data[startP + len(startStr):endP]
                    #正确答案存在个数
                    existCnt = 0
                    #正确答案下标
                    index = 0
                    for i in range(len(answerArr)):
                        if answerArr[i] in ans:
                            existCnt += 1
                            index = i
                    if existCnt == 1 :
                        print("匹配到百度汉语:{}".format(answerArr[index]))
                        return index
    #百度知识图谱
    p = data.find("data-compress=\"off\">")
    if p != -1 :
        p = data.find("setup({", p)
        if p != -1 :
            if CountItemsBeforeP(data, p) < 2:
                startStr = "fbtext: '"
                endStr = "',"

                startP = data.find(startStr, p)
                if startP != -1 :
                    endP = data.find(endStr, startP)
                    if endP != -1:
                        ans = data[startP + len(startStr):endP]
                        #正确答案存在个数
                        existCnt = 0
                        #正确答案下标
                        index = 0
                        for i in range(len(answerArr)):
                            if answerArr[i] in ans:
                                existCnt += 1
                                index = i
                        if existCnt == 1 :
                            print("匹配到百度汉语:{}".format(answerArr[index]))
                            return index
    #百度百科
    p = data.find("mu=\"https://baike.baidu.com/item/")
    if p != -1 :
        if CountItemsBeforeP(data, p) < 3:
            startStr = "百度百科</a>"
            endStr = "baike.baidu.com"

            startP = data.find(startStr, p)
            endP = data.find(endStr, startP)
            if startP != -1 and endP != -1:
                ans = data[startP + len(startStr):endP]
                ans = ans.replace("<em>", '').replace("</em>", '')
                #正确答案存在个数
                existCnt = 0
                #正确答案下标
                index = 0
                for i in range(len(answerArr)):
                    if answerArr[i] in ans:
                        existCnt += 1
                        index = i
                if existCnt == 1 :
                    print("匹配到百度百科:{}".format(answerArr[index]))
                    return index
    #百度知道最佳答案
    p = data.find("<div class=\"op_best_answer_content\">")
    if p != -1 :
        if CountItemsBeforeP(data, p) < 2:
            startStr = "<div class=\"op_best_answer_content\">"
            endStr = "<div class=\"op_best_answer_source c-clearfix\">"

            startP = p
            if startP != -1 :
                endP = data.find(endStr, startP)
                if endP != -1:
                    ans = data[startP + len(startStr):endP]
                    #正确答案存在个数
                    existCnt = 0
                    #正确答案下标
                    index = 0
                    for i in range(len(answerArr)):
                        if answerArr[i] in ans:
                            existCnt += 1
                            index = i
                    if existCnt == 1 :
                        print("匹配到百度知道最佳答案:{}".format(answerArr[index]))
                        return index
    return -1

def SearchInBaiduZhiDao(data, answerArr):
    global baiDuZhiDaoAnswerIndex, zdRatio
    startStr = "百度知道</a></h3><"
    endStr = "https://zhidao.baidu.com/que"
    startP = data.find(startStr)
    if startP != -1 :
            endP = data.find("https://zhidao.baidu.com/que", startP)
            if endP != -1:
                beforeIt = CountItemsBeforeP(data, startP)
                if beforeIt < 3:
                    ans = data[startP + len(startStr):endP]
                    existCnt = 0
                    ind = 0
                    for j in range(len(answerArr)):
                        if answerArr[j] in ans:
                            existCnt += 1
                            ind = j
                    if existCnt == 1:
                        print("匹配到百度知道概率:{}".format(answerArr[ind]))
                        baiDuZhiDaoAnswerIndex = ind
                        zdRatio = 70 - 15 * (beforeIt - 1)
                        return True
    baiDuZhiDaoAnswerIndex = -1
    zdRatio = 0
    return False

def CountItemsBeforeP(problemData, p):
    cnt = 0
    searchP = problemData.find(Str_BeforeItem)
    while searchP != -1 and searchP <= p:
        cnt += 1
        searchP = problemData.find(Str_BeforeItem, searchP + len(Str_BeforeItem))
    return cnt

if __name__ == '__main__':
    count = analyze('金坷垃三人组不包括？', ['非洲人', '欧洲人', '美国人', '日本人'])
    print("答案：", count)