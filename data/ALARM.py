from ctypes import *


class NET_DVR_SETUPALARM_PARAM(Structure):
    _fields_ = [
        ("dwSize", c_ulong),
        ("byLevel", c_byte),  # 布防优先级
        ("byAlarmInfoType", c_byte),
        ("byRetAlarmTypeV40", c_byte),
        ("byRetDevInfoVersion", c_byte),
        ("byRetVQDAlarmType", c_byte),
        ("byFaceAlarmDetection", c_byte),
        ("bySupport", c_byte),
        ("byBrokenNetHttp", c_byte),
        ("wTaskNo", c_uint16),
        ("byDeployType", c_byte),
        ("byRes1", c_byte*2),
        ("byAlarmTypeURL", c_byte),
        ("byCustomCtrl", c_byte),
    ]

class NET_DVR_ALARMINFO_V30(Structure):
    _fields_ =[
        ("dwAlarmType",c_ulong),
        ("dwAlarmInputNumber",c_ulong),
        ("byAlarmOutputNumber",c_byte*96),
        ("byAlarmRelateChannel",c_byte*64),
        ("byChannel",c_byte*64),
        ("byChannel",c_byte*33)
    ]
