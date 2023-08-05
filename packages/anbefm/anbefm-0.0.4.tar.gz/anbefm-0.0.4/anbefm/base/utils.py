import platform

def dict2class(classT, d):
    '''
    字典类型转换为类对象
    '''
    t = classT()
    t.__dict__.update(d)
    return t

def class2dict(clsi):
    return clsi.__dict__.copy()

def get_module_data_error(module_data, default_msg=None):
    default_msg = default_msg or '获取内部模块数据失败'

    if not module_data:
        return default_msg

    if not module_data.get('status'):
        return module_data.get('msg', default_msg)

def get_mdoule_data(module_data):
    if module_data:
        return module_data.get('data')


def iswin():
    sys = platform.system()
    return sys == 'Windows'

def islinux():
    sys = platform.system()
    return sys == 'Linux'