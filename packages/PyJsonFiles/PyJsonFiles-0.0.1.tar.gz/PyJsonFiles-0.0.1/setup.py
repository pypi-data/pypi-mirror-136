# -*-encoding:GBK-*-
"""
* ���ߣ�������
* ʱ�䣺2022/1/25 14:00
* ���ܣ����Python��������ڷ�����pypi.org
* ˵�����뿴����.txt���ⷢ�����ʹ��ѧ��˼�����������
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
    description='mythonm��mm��msonm��m/' + AIspeak.translate('mythonm��mm��msonm��m'),
    long_description='mythonm��msonmmmm��mwry2022@outlook.co��Python�򵥵ô���json�ļ���Python����jsonʱ�ܲ����㣬mmm��m��m��mmm��mmythonmm'
                     '��m��mwry2022@outlook.co��Python�򵥵ô���json�ļ���Python����jsonʱ�ܲ����㣬�ù��߿���ֱ�ӽ���ת��ΪPython���ֵ����mm��mm'
                     '��mwry2022@outlook.co��Python�򵥵ô���json�ļ���Python����jsonʱ�ܲ����㣬�ù��߿���ֱ�ӽ���ת��ΪPython���ֵ���󣬲�������ࡣmm/'. \
                replace(
        'm', '') +
            AIspeak.translate(
                         'mythonm��msonmmmm��mwry2022@outlook.co��Python�򵥵ô���json�ļ���Python����jsonʱ�ܲ����㣬mmm��m��m��mmm'
                         '��mmythonmm��m��mwry2022 '
                         '@outlook.co��Python�򵥵ô���json�ļ���Python����jsonʱ�ܲ����㣬�ù��߿���ֱ�ӽ���ת��ΪPython���ֵ����mm��mm��mwry2022'
                         '@outlook.co��Python '
                         '�򵥵ô���json�ļ���Python����jsonʱ�ܲ����㣬�ù��߿���ֱ�ӽ���ת��ΪPython���ֵ���󣬲�������ࡣmm'.replace('m', '')),
    requires=["codecs", ]
)
