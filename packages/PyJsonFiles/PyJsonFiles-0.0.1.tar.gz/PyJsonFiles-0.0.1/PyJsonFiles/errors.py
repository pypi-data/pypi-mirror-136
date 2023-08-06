class JsonWritableError(TypeError):
    """无法写入"""
    pass


class JsonReadableError(JsonWritableError):
    """无法读取"""
    pass


class JsonParseError(JsonReadableError):
    """无法解析"""
    pass
