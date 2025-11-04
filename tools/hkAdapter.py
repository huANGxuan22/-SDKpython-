
from ctypes import *


class HkAdapter:

    dll_path = r"D:\myproject\HK_demo\dll"

    def load_hkdll(self):
        # 载入HCCore.dll
        hccode = WinDLL(__class__.dll_path + "\\HCCore.dll")
        hcnetsdk = cdll.LoadLibrary(__class__.dll_path + "\\HCNetSDK.dll")

        return hcnetsdk

