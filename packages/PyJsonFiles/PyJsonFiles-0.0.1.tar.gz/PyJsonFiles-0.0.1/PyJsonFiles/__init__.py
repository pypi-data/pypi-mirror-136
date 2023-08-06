import codecs

try:
    from PyJsonFiles import errors
except (ImportError, ModuleNotFoundError):  # 不在PythonPath
    from . import errors
try:
    from PyJsonFiles import parser
except (ImportError, ModuleNotFoundError):  # 不在PythonPath
    from . import parser


def json_writer(file="test.json"):
    """json写器"""
    f = open(file, "r")
    if not f.writable():
        err = errors.JsonWritableError("The json file is not writable")
        raise err
    f.close()  # 关闭测试对象
    return Json(file)


def json_reader(file="test.json"):
    """json读器"""
    f = open(file, "r")
    if not f.readable():
        err = errors.JsonReadableError("The json file is not writable")
        raise err
    f.close()  # 关闭测试对象
    return Json(file)


class Json(object):
    def __init__(self, filename="test.json"):
        """初始化"""
        self.file_name = filename
        self.parsed = None  # 初始化解析字段
        self.file_r = codecs.open(filename, 'r', encoding="utf-8")
        self.parse()  # 自动解析

    def parse(self):
        """解析"""
        self.parsed = parser.parse(self.file_r)  # 解析文件

    def write(self, *kv, string=''):
        """写"""
        if len(kv) == 0:
            self.file_r.write(string)
        self.parsed[kv[0]] = kv[1]  # 修改内容
        self.file_r.close()  # 暂时关闭只读
        self.file_r = open(self.file_name, "w+")
        with self.file_r:
            self.file_r.write(str(self.parsed))  # 写入文件
        self.file_r.close()  # 关闭文件
        self.__init__(self.file_name)  # 还原

    def read(self, k=''):
        """读"""
        if not k:  # 没有键就读取全部
            return self.parsed
        else:
            return self.parsed[k]

    def close(self):
        """关闭"""
        self.file_r.close()  # 关闭文件


if __name__ == '__main__':
    print(Json("test.json").read())
if __name__ == '__main__':
    Json("test.json").write("monkey", "monvalue")
