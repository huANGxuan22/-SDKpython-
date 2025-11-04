import logging
import os
from ctypes import *


class HKAdapter:
    so_list = []

    # 加载目录下所有so文件
    def add_lib(self, path, suffix):
        files = os.listdir(path)
        for file in files:

            if not os.path.isdir(path +"\\"+ file):
                if file.endswith(suffix):
                    self.so_list.append(path +"\\"+ file)
            else:
                self.add_lib(path +"\\"+ file + "\\", suffix)

    # python 调用 sdk 指定方法
    def call_cpp(self, func_name, *args):
        for so_lib in self.so_list:
            print(so_lib, end="\t")
            try:
                lib = cdll.LoadLibrary(so_lib)

                print("load ok")
                try:
                    value = eval("lib.%s" % func_name)(*args)
                    print("调用的库：" + so_lib)
                    logging.info("执行成功,返回值：" + str(value))
                    return value
                except:
                    continue
            except:
                print("load error")
                continue
            # logging.info("库文件载入失败：" + so_lib )
        logging.error("没有找到接口！")
        return False