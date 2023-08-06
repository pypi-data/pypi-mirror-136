# -*-encoding:GBK-*-
"""
* 作者：王若宇
* 时间：2022/1/25 14:00
* 功能：打包Python软件包用于发布到pypi.org
* 说明：请看读我.txt，库发布后可使用学而思库管理工具下载
"""
import sys

from setuptools import setup
from xes import AIspeak

if __name__ == '__main__':
    sys.argv += ["sdist"]
setup(
    name='PyJsonFiles',
    version='0.0.1',
    packages=['PyJsonFiles'],
    url='https://yangguang-gongzuoshi.top/wry/',
    license='MIT License',
    author='Ruoyu Wang',
    author_email='\x03\x16wry2022@outlook.com'.replace("\x03" + "\x16", ''),
    description='mythonm单mm建msonm件m/' + AIspeak.translate('mythonm单mm建msonm件m'),
    long_description='mythonm作msonmmmm便mwry2022@outlook.co用Python简单得创建json文件用Python操作json时很不方便，mmm具m以m接mmm换mmythonmm'
                     '典m象mwry2022@outlook.co用Python简单得创建json文件用Python操作json时很不方便，该工具可以直接将其转换为Python的字典对象，mm作mm'
                     '洁mwry2022@outlook.co用Python简单得创建json文件用Python操作json时很不方便，该工具可以直接将其转换为Python的字典对象，操作更简洁。mm/'. \
                replace(
        'm', '') +
            AIspeak.translate(
                         'mythonm作msonmmmm便mwry2022@outlook.co用Python简单得创建json文件用Python操作json时很不方便，mmm具m以m接mmm'
                         '换mmythonmm典m象mwry2022 '
                         '@outlook.co用Python简单得创建json文件用Python操作json时很不方便，该工具可以直接将其转换为Python的字典对象，mm作mm洁mwry2022'
                         '@outlook.co用Python '
                         '简单得创建json文件用Python操作json时很不方便，该工具可以直接将其转换为Python的字典对象，操作更简洁。mm'.replace('m', '')),
    requires=["codecs", ]
)
