# -*- coding: utf-8 -*-
from watchdog.observers import Observer
from watchdog.events import *
import time
import json
import os

import requests
import webbrowser
import urllib.parse
# import wda

'''
原理：
1.通过charles抓包，获取 https://question.hortor.net/question/fight/findQuiz 请求响应结果数据格式如下

	{
		"data": {
			"quiz": "1919年成立于德国魏玛的著名艺术设计院校是？",
			"options": ["巴洛克", "洛可可", "包豪斯", "乌尔姆"],
			"num": 5,
			"school": "文艺",
			"type": "设计",
			"contributor": "",
			"endTime": 1515917927,
			"curTime": 1515917912
		},
		"errcode": 0
	}

2.通过charles tools--Mirro Setting 将该请求及响应结果保存到工程目录下，最终路径为 “./question.hortor.net/question/fight/findQuiz”

3.通过watchdog 监测文件变化，每当有新题出现时，会触发 FileEventHandler.on_modified 方法

4.FileEventHandler.on_modified 方法响应时，发送搜索请求，并进行判断。此处用的是（https://github.com/Skyexu/TopSup）上的 run_algorithm 方法

5.TODO: 接入WDA自动点击选项进行答题(之前试了下iOS上链接始终不稳定)

6.TODO: 答过的题保存到题库中

'''

AutoTap = False
if AutoTap:
	c = wda.Client()
	s = c.session()

# 文件变化监测
# http://blog.csdn.net/cracker_zhou/article/details/50704640
class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path,event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path,event.dest_path))

    def on_created(self, event):
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            print("file created:{0}".format(event.src_path))

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            # 文件改变，读取题目内容json
            print("directory modified:{0}".format(event.src_path))
            read_question()
        else:
            print("file modified:{0}".format(event.src_path))

# 读取问题与选项
def read_question():
    with open('./question.hortor.net/question/fight/findQuiz', encoding='utf-8') as f:
        response = json.load(f)
        question = response['data']['quiz']
        options = response['data']['options']
        # 搜索结果
        run_algorithm(2, question, options)

def run_algorithm(al_num, question, choices):
    if al_num == 0:
        open_webbrowser(question)
    elif al_num == 1:
        open_webbrowser_count(question, choices)
    elif al_num == 2:
        count_base(question, choices)

# 打开浏览器检索答案
def open_webbrowser(question):
    webbrowser.open('https://baidu.com/s?wd=' + urllib.parse.quote(question))

def open_webbrowser_count(question,choices):
    print('\n-- 方法2： 题目+选项搜索结果计数法 --\n')
    print('Question: ' + question)
    if '不是' in question:
        print('**请注意此题为否定题,选计数最少的**')

    counts = []
    for i in range(len(choices)):
        # 请求
        req = requests.get(url='http://www.baidu.com/s', params={'wd': question + choices[i]})
        content = req.text
        index = content.find('百度为您找到相关结果约') + 11
        content = content[index:]
        index = content.find('个')
        count = content[:index].replace(',', '')
        counts.append(count)
    output(choices, counts)

def count_base(question,choices):
    print('\n-- 方法3： 题目搜索结果包含选项词频计数法 --\n')
    # 请求
    req = requests.get(url='http://www.baidu.com/s', params={'wd':question})
    content = req.text
    counts = []
    print('Question: '+question)
    chosemore = True
    if '不是' in question:
        print('**请注意此题为否定题,选计数最少的**')
        chosemore = False
    for i in range(len(choices)):
        counts.append(content.count(choices[i]))
    output(choices, counts, chosemore)


def output(choices, counts, more=True):
    counts = list(map(int, counts))

    # 计数最高
    index_max = counts.index(max(counts))

    # 计数最少
    index_min = counts.index(min(counts))

    if index_max == index_min:
        print("高低计数相等此方法失效！")
        return
    if more:
        print("答案是：{0}".format(choices[index_max]))
        if AutoTap:
        	choose_answer(index_max)
    else:
        print("答案是：{0}".format(choices[index_min]))
        if AutoTap:
        	choose_answer(index_min)

# 自动选择答案
def choose_answer(num):
	# 6s上四个选项坐标分别是： （370, 735) (370, 865) (370, 1000) (370, 1144)
	# 延迟两秒，等界面刷新
	time.sleep(2)
	if num == 0:
		s.tap(370, 735)
	if num == 1:
		s.tap(370, 865)
	if num == 2:
		s.tap(370, 1000)
	if num == 3:
		s.tap(370, 1144)

if __name__ == "__main__":

	# 开始监听文件变化
    observer = Observer()
    event_handler = FileEventHandler()
    observer.schedule(event_handler,"./question.hortor.net/question/fight/",True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

