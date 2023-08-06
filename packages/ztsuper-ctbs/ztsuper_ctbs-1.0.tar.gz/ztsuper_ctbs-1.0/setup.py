from distutils.core import setup

setup(
    name="ztsuper_ctbs",#对外我们模块的名字
    version="1.0",#版本号
    description="这是我发布的第一个py模块",#描述
    author="zt",#作者
    author_email="1294582649@qq.com",#邮箱
    py_modules=["ztsuper.demo1","ztsuper.demo2"]#要对外发布的模块

)