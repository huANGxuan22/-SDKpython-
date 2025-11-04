"""
布防回调信息需要使用的结构体
包括
NET_DVR_SETUPALARM_PARAM
"""
from ctypes import *

class NET_DVR_ALARMER(Structure):
    _fields_ = [
        ("byUserIDValid",c_byte),
        ("bySerialValid", c_byte),
        ("byVersionValid", c_byte),
        ("byDeviceNameValid", c_byte),
        ("byMacAddrValid",c_byte),
        ("byLinkPortValid", c_byte),
        ("byDeviceIPValid", c_byte),
        ("bySocketIPValid", c_byte),
        ("lUserID", c_long),
        ("sSerialNumber", c_byte*48),
        ("sDeviceName", c_char*32),
        ("byMacAddr", c_byte*6),
        ("wLinkPort", c_uint16),
        ("sDeviceIP", c_char*128),
        ("sSocketIP", c_char*128),
        ("byIpProtocol", c_byte),
        ("byRes1", c_byte*2),
        ("bJSONBroken", c_byte),
        ("wSocketPort", c_uint16),
        ("byRes2", c_byte*6)
    ]


