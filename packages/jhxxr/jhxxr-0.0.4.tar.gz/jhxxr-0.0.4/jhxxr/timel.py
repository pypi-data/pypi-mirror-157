#-*- coding:utf-8 -*-
import time
import re
#当前时间
#调用方法nowtime("2022-12-12 12:12:12")
#打印结果：如2022-12-12 12:12:12的当前格式时间
def nowtime(pram):
    #2022-12-12 12:12:12
    if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',pram):
        print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
        return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    #12-12
    if re.match(r'^\d{2}-\d{2}$',pram):
        print(time.strftime("%m-%d",time.localtime()))
        return time.strftime("%m-%d",time.localtime())
    ##2022-12-12
    if re.match(r'^\d{4}-\d{2}-\d{2}$',pram):
        print(time.strftime("%Y-%m-%d",time.localtime()))
        return time.strftime("%Y-%m-%d",time.localtime())
    #12:12:12
    if re.match(r'^\d{2}:\d{2}:\d{2}$',pram):
        print(time.strftime("%H:%M:%S",time.localtime()))
        return time.strftime("%H:%M:%S",time.localtime())
    #12:12
    if re.match(r'^\d{2}:\d{2}$',pram):
        print(time.strftime("%H:%M",time.localtime()))
        return time.strftime("%H:%M",time.localtime())




#调用方法thistime(1651698305,"2022-12-12 12:12:12")
#打印结果：2022-05-05 05:05:05
def thistime(key,pram):
    #2022-12-12 12:12:12
    if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',pram):
        print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(key)))
        return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(key))
    #12-12
    if re.match(r'^\d{2}-\d{2}$',pram):
        print(time.strftime("%m-%d",time.localtime(key)))
        return time.strftime("%m-%d",time.localtime(key))
    ##2022-12-12
    if re.match(r'^\d{4}-\d{2}-\d{2}$',pram):
        print(time.strftime("%Y-%m-%d",time.localtime(key)))
        return time.strftime("%Y-%m-%d",time.localtime(key))
    #12:12:12
    if re.match(r'^\d{2}:\d{2}:\d{2}$',pram):
        print(time.strftime("%H:%M:%S",time.localtime(key)))
        return time.strftime("%H:%M:%S",time.localtime(key))
    #12:12
    if re.match(r'^\d{2}:\d{2}$',pram):
        print(time.strftime("%H:%M",time.localtime(key)))
        return time.strftime("%H:%M",time.localtime(key))
    




if __name__=='__main__':
    thistime(1651698305,"2022-12-12 12:12:12")