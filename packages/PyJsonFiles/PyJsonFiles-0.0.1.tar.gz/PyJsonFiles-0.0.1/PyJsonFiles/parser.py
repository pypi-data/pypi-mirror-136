try:
    from PyJsonFiles import errors
except (ImportError, ModuleNotFoundError):  # 不在PythonPath
    from . import errors


def parse(file):  # =open('test.json')):
    # file=open(file,'r')
    xf = file.read()
    print(xf)
    try:
        returner = dict(eval(xf))
    except Exception:  # 不能解析
        err = errors.JsonParseError("Cannot parse json" + str(file))
        raise err
        pass
    file.close()
    return returner
