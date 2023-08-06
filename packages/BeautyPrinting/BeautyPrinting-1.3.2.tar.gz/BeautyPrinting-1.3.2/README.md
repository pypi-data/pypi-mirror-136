# 欢迎下载BeautyPrinting！
## 你是否想要拥有幻彩的打印输出？
```python
from BeautyPrinting.BtPrint import btprint

btprint('Colorful Hello World!', color='cyan', bgcolor='black')
```
###### 两行代码，就可以拥有炫彩的“Hello World”
## 你是否想要拥有炫酷的加载进度条？
```python
from BeautyPrinting.ProgressBar import loading_bar

loading_bar('Loading......', items=50, color='cyan')
```
###### 两行代码，轻松拥有多彩的加载条
## 新功能：enlighten progress bar
```python
from BeautyPrinting.ProgressBar import enlighten_loading_bar

enlighten_loading_bar(text='Loading', items=200, sleep=0.01, color='cyan')
```
```python
from BeautyPrinting.ProgressBar import enlighten_loading_bars

enlighten_loading_bars(5, use_list=False, text='Loading......', items=200, sleep=0.01, color='cyan')
```
###### 抽象Enlighten接口，摆脱复杂的Enlighten API
## 赶紧下载我们BeautyPrinting吧！一定能满足您的美学需求！