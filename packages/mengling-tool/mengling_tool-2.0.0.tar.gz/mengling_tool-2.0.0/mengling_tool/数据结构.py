from .__数据结构__.环状双向链表 import LinkedLooplist
from .__数据结构__.同步资源_多组 import Resource
from .__数据结构__.同步资源_迭代 import Synchro
from .__数据结构__.动态缓存 import Cache
from .__数据结构__.链表 import LinkedList
from .__数据结构__.资源池 import ResourcePool
import traceback


# 捕获装饰器方法
def tryFunc_args(iftz=True, except_return_value=None):
    def temp(func):
        def temp_ch(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                if iftz:
                    traceback.print_exc()
                return except_return_value

        return temp_ch

    return temp
