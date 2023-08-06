# 欢迎下载EasyThreadings dev试用版！
## 入门：如何在EasyThreads中创建线程？
```python
from EasyThreadings import thread

@thread
def hello_thread():
    print('Hello from threading!')

hello_thread()
```
#无需更多代码，每次调用自动启动新线程
## 高级：如何控制线程？
```python
from EasyThreadings import thread
from EasyThreadings.More import join

@thread(name='thread')
def hello_thread():
    print('Hello from threading!')

hello_thread()
join('thread')
```
#利用name支持，轻松控制线程
## 新功能：现在支持阻塞函数
```python
from EasyThreadings import thread
from EasyThreadings.More import join_func

@thread
def hello_thread():
    print('Hello from threading!')

hello_thread()
join_func(hello_thread)
```
# 赶紧下载我们的EasyThreadings吧！