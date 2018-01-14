# brainking
头脑王者辅助

###原理：
1.在答题页面通过 [Charles](http://blog.devtang.com/2015/11/14/charles-introduction/) 抓包，获取 https://question.hortor.net/question/fight/findQuiz 请求响应结果数据格式如下


![响应结果](http://upload-images.jianshu.io/upload_images/870531-3e223f612c731c9c.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```json
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
```

2.通过 **工具栏->charles tools->Mirro Setting** 将该请求响应结果保存到工程目录下，最终路径为 **“./question.hortor.net/question/fight/findQuiz”**
注意： **Save to** 一栏需要设置为工程目录所在路径

![设置Mirror](http://upload-images.jianshu.io/upload_images/870531-70be6f4488ad44d7.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![设置响应数据的本地地址](http://upload-images.jianshu.io/upload_images/870531-8f0b7d2e8f93a0ee.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

3.通过 `watchdog` 监测`./question.hortor.net/question/fight/findQuiz`目录下文件变化，每当有新题出现时，会触发 `FileEventHandler.on_modified` 方法

4.`FileEventHandler.on_modified` 方法响应时，发送搜索请求，并进行判断。此处用的是 [答题辅助](https://github.com/Skyexu/TopSup) 上的 `run_algorithm` 方法

![读取答案](http://upload-images.jianshu.io/upload_images/870531-45021cc84f51e974.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

5.TODO: 接入WDA自动点击选项进行答题(之前试了下iOS上链接始终不稳定，并且存在延迟)

6.TODO: 答过的题保存到题库中
