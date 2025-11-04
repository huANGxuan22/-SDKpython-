from ctypes import *
import time


# 云台控制命令常量
class PTZCommand:
    LIGHT_PWRON = 2  # 灯光开关
    WIPER_PWRON = 3  # 雨刷开关
    PAN_PWRON = 4  # 云台电源
    HEATER_PWRON = 5  # 加热器开关
    AUX_PWRON1 = 6  # 辅助开关1
    AUX_PWRON2 = 7  # 辅助开关2
    ZOOM_IN = 11  # 焦距变大（望远）
    ZOOM_OUT = 12  # 焦距变小（广角）
    FOCUS_NEAR = 13  # 焦点近调
    FOCUS_FAR = 14  # 焦点远调
    IRIS_OPEN = 15  # 光圈扩大
    IRIS_CLOSE = 16  # 光圈缩小
    TILT_UP = 21  # 云台上仰
    TILT_DOWN = 22  # 云台下俯
    PAN_LEFT = 23  # 云台左转
    PAN_RIGHT = 24  # 云台右转
    UP_LEFT = 25  # 云台上仰和左转
    UP_RIGHT = 26  # 云台上仰和右转
    DOWN_LEFT = 27  # 云台下俯和左转
    DOWN_RIGHT = 28  # 云台下俯和右转
    PAN_AUTO = 29  # 云台自动扫描


class PTZController:
    def __init__(self, hksdk):
        self.hksdk = hksdk
        self.user_id = -1
        self.channel = 1
        self._setup_ptz_functions()

    def _setup_ptz_functions(self):
        """设置云台控制函数的参数类型"""
        # 设置云台控制函数原型
        self.hksdk.NET_DVR_PTZControlWithSpeed_Other.argtypes = [
            c_long,  # lUserID - 用户ID
            c_long,  # lChannel - 通道号
            c_uint,  # dwPTZCommand - 云台命令
            c_uint,  # dwStop - 停止标志 (0-开始, 1-停止)
            c_uint  # dwSpeed - 速度 (1-7)
        ]
        self.hksdk.NET_DVR_PTZControlWithSpeed_Other.restype = c_bool

    def set_user_info(self, user_id, channel=1):
        """设置用户ID和通道号"""
        self.user_id = user_id
        self.channel = channel

    def control(self, command, stop, speed):
        """
        控制云台运动

        参数:
            command: 云台控制命令
            stop: 0-开始, 1-停止
            speed: 速度值 (1-7)

        返回:
            bool: 操作是否成功
        """
        if self.user_id == -1:
            print("错误：请先设置用户ID")
            return False

        result = self.hksdk.NET_DVR_PTZControlWithSpeed_Other(
            c_long(self.user_id),
            c_long(self.channel),
            c_uint(command),
            c_uint(stop),
            c_uint(speed)
        )

        if not result:
            error_code = self.hksdk.NET_DVR_GetLastError()
            print(f"云台控制失败，错误码: {error_code}")
            return False
        return True

    def move(self, direction, speed=5, duration=0):
        """
        控制云台移动（带自动停止功能）

        参数:
            direction: 移动方向
            speed: 移动速度 (1-7)
            duration: 持续时间(秒)，0表示不自动停止
        """
        # 开始移动
        success = self.control(direction, 0, speed)

        # 如果设置了持续时间，自动停止
        if success and duration > 0:
            time.sleep(duration)
            self.control(direction, 1, speed)

        return success

    def stop(self, direction):
        """停止云台运动"""
        return self.control(direction, 1, 0)

    def test_all_movements(self):
        """测试所有云台运动功能"""
        print("开始云台控制全面测试...")

        movements = [
            ("右转", PTZCommand.PAN_RIGHT, 3),
            ("左转", PTZCommand.PAN_LEFT, 3),
            ("上仰", PTZCommand.TILT_UP, 2),
            ("下俯", PTZCommand.TILT_DOWN, 2),
            ("变焦放大", PTZCommand.ZOOM_IN, 2),
            ("变焦缩小", PTZCommand.ZOOM_OUT, 2),
        ]

        for name, command, duration in movements:
            print(f"测试: {name}...")
            if self.move(command, speed=4, duration=duration):
                print(f"{name}测试完成")
            else:
                print(f"{name}测试失败")
            time.sleep(1)

        print("云台控制全面测试完成！")

    def preset_point_control(self, preset_number, action=0):
        """
        预置点控制（需要设备支持）

        参数:
            preset_number: 预置点编号 (1-255)
            action: 0-设置, 1-调用, 2-删除
        """
        if action == 0:  # 设置预置点
            result = self.hksdk.NET_DVR_SetPreset(self.user_id, self.channel, preset_number)
        elif action == 1:  # 调用预置点
            result = self.hksdk.NET_DVR_GoToPreset(self.user_id, self.channel, preset_number)
        elif action == 2:  # 删除预置点
            result = self.hksdk.NET_DVR_ClearPreset(self.user_id, self.channel, preset_number)
        else:
            print("错误的预置点操作类型")
            return False

        if not result:
            error_code = self.hksdk.NET_DVR_GetLastError()
            print(f"预置点操作失败，错误码: {error_code}")
            return False
        return True