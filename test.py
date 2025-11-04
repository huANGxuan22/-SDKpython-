from tools.hkAdapter import HkAdapter
from data import NET_DVR_Login_V40
from ctypes import *
from data import MSesGCallback
from data import ALARM
from data import PTZController, PTZCommand
import time


class HikvisionCamera:
    def __init__(self):
        self.hkadapter = HkAdapter()
        self.hksdk = None
        self.user_id = -1
        self.ptz_controller = None
        self.alarm_handle = -1

    def initialize(self):
        """初始化SDK"""
        print("-----------初始化SDK---------")
        self.hksdk = self.hkadapter.load_hkdll()

        if not self.hksdk.NET_DVR_Init():
            error_code = self.hksdk.NET_DVR_GetLastError()
            print(f"SDK初始化失败，错误码: {error_code}")
            return False

        # 设置连接超时时间（可选）
        if not self.hksdk.NET_DVR_SetConnectTime(2000, 1):
            print("设置连接时间失败，但继续执行")

        print("SDK初始化成功")
        return True

    def login(self, ip, username, password, port=8000):
        """登录设备"""
        if self.hksdk is None:
            print("错误：请先初始化SDK")
            return False

        print(f"尝试登录设备 - IP: {ip}, 端口: {port}, 用户名: {username}")

        # 准备登录信息
        login_info = NET_DVR_Login_V40.NET_DVR_USER_LOGIN_INFO()
        device_info = NET_DVR_Login_V40.NET_DVR_DEVICEINFO_V40()

        # 清零结构体
        memset(byref(login_info), 0, sizeof(login_info))
        memset(byref(device_info), 0, sizeof(device_info))

        # 设置登录参数
        login_info.wPort = port
        login_info.bUseAsynLogin = 0  # 同步登录

        # 编码字符串
        login_info.sDeviceAddress = ip.encode('utf-8')
        login_info.sUserName = username.encode('utf-8')
        login_info.sPassword = password.encode('utf-8')

        # 执行登录
        self.user_id = self.hksdk.NET_DVR_Login_V40(byref(login_info), byref(device_info))

        if self.user_id == -1:
            error_code = self.hksdk.NET_DVR_GetLastError()
            print(f"登录失败，错误码: {error_code}")
            return False
        else:
            print(f"登录成功，用户ID: {self.user_id}")

            # 初始化云台控制器
            self.ptz_controller = PTZController(self.hksdk)
            self.ptz_controller.set_user_info(self.user_id)

            return True

    def setup_alarm(self):
        """设置报警回调"""
        if self.user_id == -1:
            print("错误：请先登录设备")
            return False

        # 设置报警回调函数
        callback_result = self.hksdk.NET_DVR_SetDVRMessageCallBack_V31(self.alarm_callback, None)
        if callback_result == -1:
            error_code = self.hksdk.NET_DVR_GetLastError()
            print(f"设置报警回调失败，错误码: {error_code}")
            return False
        else:
            print("报警回调设置成功")

        # 设置布防参数
        alarm_param = ALARM.NET_DVR_SETUPALARM_PARAM()
        alarm_param.dwSize = sizeof(ALARM.NET_DVR_SETUPALARM_PARAM)
        alarm_param.byLevel = 0
        alarm_param.byAlarmInfoType = 1

        # 启动布防
        self.alarm_handle = self.hksdk.NET_DVR_SetupAlarmChan_V41(self.user_id, byref(alarm_param))
        if self.alarm_handle < 0:
            error_code = self.hksdk.NET_DVR_GetLastError()
            print(f"布防失败，错误码: {error_code}")
            return False
        else:
            print("布防成功")
            return True

    def cleanup_alarm(self):
        """清理报警设置"""
        if self.alarm_handle >= 0:
            result = self.hksdk.NET_DVR_CloseAlarmChan_V30(self.alarm_handle)
            if result == -1:
                error_code = self.hksdk.NET_DVR_GetLastError()
                print(f"撤防失败，错误码: {error_code}")
            else:
                print("撤防成功")
            self.alarm_handle = -1

    def logout(self):
        """登出设备"""
        if self.user_id != -1:
            result = self.hksdk.NET_DVR_Logout(self.user_id)
            if result == -1:
                error_code = self.hksdk.NET_DVR_GetLastError()
                print(f"登出失败，错误码: {error_code}")
            else:
                print("登出成功")
            self.user_id = -1

    def cleanup(self):
        """清理SDK"""
        if self.hksdk:
            self.hksdk.NET_DVR_Cleanup()
            print("SDK清理完成")

    @CFUNCTYPE(c_int, c_long, MSesGCallback.NET_DVR_ALARMER, c_char_p, c_ulong, c_void_p)
    def alarm_callback(self, lCommand, pAlarmer, pAlarmInfo, dwBufLen, pUser):
        """报警回调函数"""
        print(f"收到报警信息，类型: {lCommand}, 发送者: {pAlarmer.lUserID}")

        if lCommand == 0x4000:  # COMM_ALARM_V30
            print("消息类型: COMM_ALARM_V30", end=" --> ")

            # 解析报警信息
            alarm_info = ALARM.NET_DVR_ALARMINFO_V30()
            if dwBufLen >= sizeof(alarm_info):
                memmove(byref(alarm_info), pAlarmInfo, sizeof(alarm_info))

                if alarm_info.dwAlarmType == 3:
                    print("子事件: 移动侦测")
                else:
                    print(f"子事件: {alarm_info.dwAlarmType}")
            else:
                print("报警信息长度不足")
        else:
            print(f"未知消息类型: {lCommand}")

        return 1

    def test_ptz_operations(self):
        """测试云台操作"""
        if self.ptz_controller is None:
            print("错误：云台控制器未初始化")
            return

        print("-----------开始云台控制测试---------")

        # 测试各种云台动作
        test_actions = [
            ("右转", PTZCommand.PAN_RIGHT, 3),
            ("左转", PTZCommand.PAN_LEFT, 3),
            ("上仰", PTZCommand.TILT_UP, 2),
            ("下俯", PTZCommand.TILT_DOWN, 2),
            ("变焦放大", PTZCommand.ZOOM_IN, 2),
            ("变焦缩小", PTZCommand.ZOOM_OUT, 2),
        ]

        for name, command, duration in test_actions:
            print(f"测试: {name}...")
            if self.ptz_controller.move(command, speed=4, duration=duration):
                print(f"{name}测试完成")
            else:
                print(f"{name}测试失败")
            time.sleep(1)

        print("云台控制测试完成")

    def run_complete_test(self, ip, username, password):
        """运行完整测试"""
        try:
            # 1. 初始化SDK
            if not self.initialize():
                return

            # 2. 登录设备
            if not self.login(ip, username, password):
                return

            # 3. 测试云台控制
            self.test_ptz_operations()

            # 4. 设置报警并等待
            print("-----------设置报警监控---------")
            if self.setup_alarm():
                print("等待报警信息（30秒）...")
                time.sleep(30)
                self.cleanup_alarm()

        except Exception as e:
            print(f"测试过程中发生异常: {e}")
        finally:
            # 确保资源被正确清理
            self.cleanup_alarm()
            self.logout()
            self.cleanup()


def interactive_ptz_test(camera):
    """交互式云台控制测试"""
    if camera.ptz_controller is None:
        print("错误：云台控制器未初始化")
        return

    print("\n=== 交互式云台控制测试 ===")
    print("命令列表:")
    print("  up    - 云台上仰")
    print("  down  - 云台下俯")
    print("  left  - 云台左转")
    print("  right - 云台右转")
    print("  zin   - 变焦放大")
    print("  zout  - 变焦缩小")
    print("  stop  - 停止所有运动")
    print("  auto  - 自动测试所有动作")
    print("  quit  - 退出测试")

    command_map = {
        'up': PTZCommand.TILT_UP,
        'down': PTZCommand.TILT_DOWN,
        'left': PTZCommand.PAN_LEFT,
        'right': PTZCommand.PAN_RIGHT,
        'zin': PTZCommand.ZOOM_IN,
        'zout': PTZCommand.ZOOM_OUT
    }

    while True:
        cmd = input("\n请输入命令: ").strip().lower()

        if cmd == 'quit':
            break
        elif cmd == 'auto':
            camera.test_ptz_operations()
        elif cmd == 'stop':
            # 停止所有可能的运动
            for direction in command_map.values():
                camera.ptz_controller.stop(direction)
            print("所有运动已停止")
        elif cmd in command_map:
            direction = command_map[cmd]
            try:
                duration = float(input("请输入持续时间(秒): "))
                speed = int(input("请输入速度(1-7): "))
                camera.ptz_controller.move(direction, speed, duration)
            except ValueError:
                print("输入无效，请输入数字")
        else:
            print("未知命令，请重新输入")


if __name__ == "__main__":
    # 创建摄像头实例
    camera = HikvisionCamera()

    # 设备信息
    ip = "192.168.110.110"
    username = "admin"
    password = "Xtjc.132"

    # 运行完整测试
    camera.run_complete_test(ip, username, password)

    # 如果你想进行交互式测试，可以取消下面的注释
    # 注意：需要先确保登录成功
    # if camera.user_id != -1:
    #     interactive_ptz_test(camera)