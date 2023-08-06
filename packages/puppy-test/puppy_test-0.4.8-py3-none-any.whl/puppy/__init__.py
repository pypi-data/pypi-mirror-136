__version__ = "0.4.8"
__host__ = "http://172.32.4.219/puppy_test"

# __host__="http://r4735hqh7.hn-bkt.clouddn.com"
import os
import warnings
from urllib import request


def to_int(version):
    a = version.replace(".", "")
    return int(a)


def get_server_version() -> str:
    """从服务器取到最新的版本"""
    read = os.popen("pip list -o -i http://172.32.4.219/rep/simple --trusted-host 172.32.4.219 --format=columns")
    # read = os.popen("pip list -o --format=columns")
    for _l in read.readlines():
        if "puppy-test" in _l:
            splitted = _l.split()
            return splitted[2]
    return get_version()


def get_version() -> str:
    """获取当前框架版本"""
    global __version__
    return __version__


def upgrade_puppy_test():
    global __host__
    print("获取服务器puppy-test框架的版本中...")
    version = get_server_version()
    filename = "puppy_test-{}-py3-none-any.whl".format(version)
    if version is None:
        print("版本为空")
        return 0
    puppy_test_url = __host__ + "/{}".format(filename)
    print("下载升级文件中...")
    request.urlretrieve(puppy_test_url, filename)
    print("升级中...")
    re=os.system('pip install "{}"'.format(filename))
    os.remove(filename)
    return re


def check_version(version):
    if to_int(version) > to_int(get_version()):
        warnings.warn("puppy_test框架版本落后于当前工程版本，请使用以下命令升级puppy_test框架：\n     pip3 install -U puppy-test -i http://172.32.4.219/rep/simple/ --trusted-host 172.32.4.219", UserWarning)
    if to_int(version) < to_int(get_version()):
        warnings.warn('puppy_test框架版本高于当前工程版本，请使用puppy update命令进行更新！', UserWarning)
