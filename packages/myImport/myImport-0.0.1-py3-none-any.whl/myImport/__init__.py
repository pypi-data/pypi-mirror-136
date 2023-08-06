'''
Author: your name
Date: 2022-01-17 17:10:42
LastEditTime: 2022-01-29 12:15:00
LastEditors: Liu Yancheng
Description: 
FilePath: \myImport\__init__.py
'''

from myImport.valueInfo import valueInfo

__version__ = "0.0.1"
__description__="for looking up information of values"
__author__ = "Liu Yancheng"
__author_email__ = "Liu Yancheng"
__url__ = "http://gitee.com/qq1418381215/myImport"
# __init__.py 文件定义了包的属性和方法。其实它可以什么也不定义；可以只是一个空文件，但是必须存在。
# 如果 __init__.py 不存在，这个目录就仅仅是一个目录，而不是一个包，它就不能被导入或者包含其它的模块和嵌套包。

'''
.
└── mypackage
    ├── subpackage_1
    │   ├── test11.py
    │   └── test12.py
    ├── subpackage_2
    │   ├── test21.py
    │   └── test22.py
    └── subpackage_3
        ├── test31.py
        └── test32.py
    
没有这个文件：
from mypackage.subpackage_1 import test11
from mypackage.subpackage_1 import test12
from mypackage.subpackage_2 import test21
from mypackage.subpackage_2 import test22
from mypackage.subpackage_3 import test31
from mypackage.subpackage_3 import test32


有这个文件：
.
└── mypackage
    ├── __init__.py
    ├── subpackage_1
    │   ├── test11.py
    │   └── test12.py
    ├── subpackage_2
    │   ├── test21.py
    │   └── test22.py
    └── subpackage_3
        ├── test31.py
        └── test32.py
        
在init里面写
from mypackage.subpackage_1 import test11
注意这里还是要从根目录写起
则import mypackage的时候，就会导入这个test11了


在init里面写__all__ = ['subpackage_1', 'subpackage_2']
则写from mypackage import *的时候，就会有'subpackage_1', 'subpackage_2'
等价于from mypackage import subpackage_1, subpackage_2

所以可以写__all__ = ['os', 'sys', 're', 'urllib']

没有from
import subpackage1.a # 将模块subpackage.a导入全局命名空间，例如访问a中属性时用subpackage1.a.attr

有from
from subpackage1 import a #　将模块a导入全局命名空间，例如访问a中属性时用a.attr_a
from subpackage.a import attr_a # 将模块a的属性直接导入到命名空间中，例如访问a中属性时直接用attr_a 

使用from语句可以把模块直接导入当前命名空间，from语句并不引用导入对象的命名空间，而是将被导入对象直接引入当前命名空间。


对于函数
import arithmetic.add
import arithmetic.sub as sub

from arithmetic.mul import mul
from arithmetic import dev

def letscook(x, y, oper):
    r = 0
    if oper == "+":
        r = arithmetic.add.add(x, y)
    elif oper == "-":
        r = sub.sub(x, y)
    elif oper == "*":
        r = mul(x, y)
    else:
        r = dev.dev(x, y)
'''
