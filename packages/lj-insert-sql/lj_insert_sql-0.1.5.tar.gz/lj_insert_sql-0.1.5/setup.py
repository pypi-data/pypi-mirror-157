from setuptools import setup, find_packages
from distutils.core import setup

setup(
    name = "lj_insert_sql",# 对外的模块名字
    version = "0.1.5",# 版本号
    keywords = ("test"),
    description = "lj add sql！",# 信息描述
    long_description = "lj_sql package",# 详细描述
    license = "MIT Licence", # 许可证

    url = "http://songbaobao.com", # 一个URL（假的）
    author = "jiaochanghao",# 作者
    author_email = "2154195820@qq.com",# 这是宋宝宝的邮箱啊（不是真的）

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = [],

    scripts = [],
    entry_points = {
        'console_scripts': [
            'test = test.help:main'
        ]
    },
    py_modules=["package.lj_sqlpackage"] # 要发布的模块
)

# 打包模块
# python3 setup.py sdist
# 上传
# python3 -m twine upload --repository pypi dist/*

