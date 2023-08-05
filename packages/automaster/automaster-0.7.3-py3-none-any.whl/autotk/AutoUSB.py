import os
import sys
import time
import json
from win32com.directsound import directsound
import usb1
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mbox
import winreg
import serial.tools.list_ports
import win32api, win32con
import win32com.client
from ctypes import POINTER
from comtypes import client, IUnknown, Structure, GUID, COMMETHOD, HRESULT, BSTR, COMError, COMObject
from comtypes.automation import VARIANT
from comtypes.persist import IPropertyBag, IErrorLog
import re
from gen.DirectShowLib import ICreateDevEnum
import serial.tools.list_ports
from autotk.AutoCoreLite import logger
import traceback

# 定义常量
bind_id = {
    "VID_1902&PID_8301": "LED", "VID_1BCF&PID_0B09": "LED", "VID_0BDA&PID_5843": "LED",
    "VID_0D8C&PID_0014": "SPDIF", "VID_1B3F&PID_2008": "SPDIF",
    "VID_1E4E&PID_7016": "HDMI",
    "VID_1E4E&PID_7111": "HDMI",
    "VID_048D&PID_9323": "HDMI",
    "VID_534D&PID_2109": "AV",
    "VID_067B&PID_2303": "COM","VID_0403&PID_6001": "COM",
    "VID_E851&PID_1002": "SCAN",
    "VID_1A86&PID_7523": "IR",  # Button_COM 与红外发射冲突了
    (255, 66, 1): "DUT"  # 特殊绑定ADB接口类(匹配设备Id)
}
com_groupname = {"COM": "电压模组", "SCAN": "扫码模组", "IR": "红外模组"}  # 定义串口分组名称
rec_groupname = {"AV": "AV音频", "HDMI": "HDMI音频", "SPDIF": "光纤音频"}  # 定义音频分组名称
cam_groupname = {"AV": "AV视频", "HDMI": "HDMI视频", "LED": "LED视觉"}  # 定义视频分组名称
groudid_name = {"HDMI": "HDMI采集卡", "SPDIF": "光纤采集", "AV": "AV采集组", "LED": "LED摄像头", "SCAN": "扫码模组",
                "IR": "红外模组", "COM": "电压模组"}  # 定义设备描述
tagid_groupname = {"HDMI_AUDIO": "HDMI音频", "HDMI_VIDEO": "HDMI视频", "AV_AUDIO": "AV音频", "AV_VIDEO": "AV视频",
                   "SPDIF_AUDIO": "光纤音频", "LED_TEST": "LED视觉", "IR_TEST": "红外模组", "SCANNER": "扫码模组",
                   "DVB_VOLT": "电压模组", "HDMI_VOLT": "电压模组"}  # 定义plan测试项与分组名称绑定
_system_device_enum = client.CreateObject('{62BE5D10-60EB-11d0-BD3B-00A0C911CE86}', interface=ICreateDevEnum)


def get_device_information(moniker, info_names=["DevicePath"]):
    storage = moniker.RemoteBindToStorage(None, None, IPropertyBag._iid_)  # pylint: disable=protected-access
    bag = storage.QueryInterface(interface=IPropertyBag)
    info = {}
    for prop in info_names:
        try:
            error = POINTER(IErrorLog)
            variant = VARIANT("")
            v = bag.Read(pszPropName=prop, pVar=variant, pErrorLog=error())
            if ("vid_" in v):
                # pattern = re.compile(r"usb#(\S*)\\")
                pattern = re.compile(r"(usb#\S*)#{")
                list = pattern.findall(v)
                if (list):
                    v = list[0].upper().replace("#", "\\")
            info[prop] = v
        except Exception:
            print("prop.Read(%s) failed" % prop)
    return info


# def get_audio_devices():
#     CLSID_AudioInputDeviceCategory = GUID('{33D9A762-90C8-11D0-BD43-00A0C911CE86}')
#     class_enum = _system_device_enum.CreateClassEnumerator(CLSID_AudioInputDeviceCategory, 0)
#     fetched = True
#     devices_info = {}
#     index = 0
#     while fetched:
#         try:
#             moniker, fetched = class_enum.RemoteNext(1)
#             # print("fetched=%s, moniker=%s"%(fetched, moniker))
#             if fetched and moniker:
#                 info = get_device_information(moniker, ["FriendlyName"])
#                 devices_info[index] = info
#                 index += 1
#         except ValueError:
#             # print("device %i not found"%index)
#             break
#     return devices_info


def get_video_devices():
    CLSID_VideoInputDeviceCategory = GUID("{860BB310-5D01-11d0-BD3B-00A0C911CE86}")
    class_enum = _system_device_enum.CreateClassEnumerator(CLSID_VideoInputDeviceCategory, 0)
    fetched = True
    devices_info = {}
    index = 0
    while fetched:
        try:
            moniker, fetched = class_enum.RemoteNext(1)
            # print("fetched=%s, moniker=%s"%(fetched, moniker))
            if fetched and moniker:
                info = get_device_information(moniker, ["DevicePath"])
                # print(get_device_information(moniker,["FriendlyName"]))
                devices_info[index] = info
                index += 1
        except ValueError:
            # print("device %i not found"%index)
            break
    # print(devices_info)
    return devices_info


def listen_usb(dev_id_dict):
    _listen_port = {}
    for id, info in dev_id_dict.items():
        if "VID" in id:
            port = info.get("Port", "")
            vpid = info.get("ID", "")
            if port and vpid:
                _listen_port[(port, vpid)] = id
    # print(_listen_port)
    with usb1.USBContext() as context:
        for device in context.getDeviceList(skip_on_error=True):
            vid = "%04X" % device.getVendorID()
            pid = "%04X" % device.getProductID()
            vid_pid = "VID_%s&PID_%s" % (vid, pid)
            bus = device.getBusNumber()
            subport = device.getPortNumberList()
            portpath = [bus] + subport
            portname = ".".join([str(i) for i in portpath])
            if (portname, vid_pid) in _listen_port:
                _listen_port.pop((portname, vid_pid))
    if _listen_port:
        err_log = []
        for id in _listen_port.values():
            info = dev_id_dict.get(id, {})
            # print(info)
            gname = groudid_name.get(info.get("Group", ""), "未定义")
            msg = "[%s]%s %s" % (info.get("Port", ""), gname, info.get("Name", ""))
            err_log.append(msg)
        return err_log
    return None


def scan_video(dev_id_dict):
    video_info = get_video_devices()
    bind_cap = {}
    _local_bind = {}
    for c, d in video_info.items():
        DevicePath = d.get('DevicePath', "")
        if DevicePath:
            if not dev_id_dict.get(DevicePath, {}):
                dev_id_dict[DevicePath] = {}
            _VPid = re.compile(r"VID_\w+&PID_\w+").findall(DevicePath)
            if _VPid:
                dev_id_dict[DevicePath]["ID"] = _VPid[0]
                _group = bind_id.get(_VPid[0], "Error")
                dev_id_dict[DevicePath]["Group"] = _group
                dev_id_dict[DevicePath]["GroupName"] = cam_groupname.get(_group, "未知")
                dev_id_dict[DevicePath]["CapId"] = c
                bind_cap[DevicePath] = c
                FName, Location = get_campath_reg(DevicePath)
                dev_id_dict[DevicePath]["local"] = Location
                dev_id_dict[DevicePath]["Name"] = FName
                _local_bind[Location] = DevicePath
    return bind_cap, _local_bind


def get_recpath_reg(devpath):
    try:
        keystr = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\MMDevices\\Audio\\Capture\\%s\\Properties" % devpath
        tagkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, keystr)
        # portinfo,valuetype=winreg.QueryValueEx(tagkey, "{b3f8fa53-0004-438e-9003-51a46e139bfc},6")  # name
        value, valuetype = winreg.QueryValueEx(tagkey, "{b3f8fa53-0004-438e-9003-51a46e139bfc},2")  # DevicePath
        # print(devpath,"=",value)
        DevicePath = value.split(".")[-1]
        keystr = "SYSTEM\\CurrentControlSet\\Enum\\%s" % DevicePath
        tagkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, keystr)
        value, valuetype = winreg.QueryValueEx(tagkey, "LocationInformation")

        if ".000" in value:
            Location_l = []
            _ul = value.split(".")
            for i in range(len(_ul)):
                _last = int(_ul[-i])
                if Location_l:
                    if (_last):
                        Location_l.insert(0, str(_last))
                    else:
                        break
                else:
                    if _last:
                        Location_l.append(str(_last))
            Location = ".".join(Location_l)
        else:
            Location = value
        winreg.CloseKey(tagkey)
        return DevicePath, Location
    except:
        return "", ""


def get_campath_reg(DevicePath):
    try:
        keystr = "SYSTEM\\CurrentControlSet\\Enum\\%s" % DevicePath
        tagkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, keystr)
        value, valuetype = winreg.QueryValueEx(tagkey, "LocationInformation")
        FName, valuetype = winreg.QueryValueEx(tagkey, "FriendlyName")
        if ".000" in value:
            Location_l = []
            _ul = value.split(".")
            for i in range(len(_ul)):
                _last = int(_ul[-i])
                if Location_l:
                    if (_last):
                        Location_l.insert(0, str(_last))
                    else:
                        break
                else:
                    if _last:
                        Location_l.append(str(_last))
            Location = ".".join(Location_l)
        else:
            Location = value
        winreg.CloseKey(tagkey)
        return FName, Location
    except:
        return "", ""


def scan_audio(dev_id_dict):
    devices = directsound.DirectSoundCaptureEnumerate()
    _local_bind = {}
    bind_iid = {}
    for iid, name, sid in devices:
        if (iid):
            sidstr = sid.split(".")[-1]
            DevicePath, Location = get_recpath_reg(sidstr)
            if not dev_id_dict.get(DevicePath, {}):
                dev_id_dict[DevicePath] = {}
            _VPid = re.compile(r"VID_\w+&PID_\w+").findall(DevicePath)
            if _VPid:
                dev_id_dict[DevicePath]["ID"] = _VPid[0]
                _group = bind_id.get(_VPid[0], "Error")
                dev_id_dict[DevicePath]["Group"] = _group
                dev_id_dict[DevicePath]["GroupName"] = rec_groupname.get(_group, "未知")
                dev_id_dict[DevicePath]["Name"] = name
                dev_id_dict[DevicePath]["sid"] = sid
                dev_id_dict[DevicePath]["sidstr"] = sidstr
                dev_id_dict[DevicePath]["iid"] = iid
                dev_id_dict[DevicePath]["local"] = Location
                _local_bind[Location] = DevicePath
                bind_iid[DevicePath] = iid
    return bind_iid, _local_bind


def get_bind_cam(dev_id_dict, dut_port, tagid):
    try:
        _Sta = dev_id_dict.get('DutSta', {}).get(dut_port, "")
        group_name = tagid_groupname.get(tagid, "")
        if _Sta and group_name:
            for retry in range(3):
                dev_now, _local = scan_video(dev_id_dict)
                for id, info in dev_id_dict.items():
                    if "VID" in id and id in dev_now:
                        if info.get("Sta", "") == _Sta and info.get("GroupName", "") == group_name:
                            dev_port = info.get("Port", "")
                            tag = dev_now.get(id, None)
                            logger.debug("%s(%s)->%s(%s)=%s" % (dut_port, _Sta, dev_port, id, tag))
                            return tag, id, info
        return None, "", {}
    except Exception as e:
        logger.error(str(e))
        return None, str(e), {}


def get_bind_com(dev_id_dict, dut_port, tagid):
    try:
        _Sta = dev_id_dict.get('DutSta', {}).get(dut_port, "")
        group_name = tagid_groupname.get(tagid, "")
        if _Sta and group_name:
            for retry in range(3):
                dev_now, _local = scan_serial(dev_id_dict)
                for id, info in dev_id_dict.items():
                    if "VID" in id and id in dev_now:
                        if info.get("Sta", "") == _Sta and info.get("GroupName", "") == group_name:
                            dev_port = info.get("Port", "")
                            tag = dev_now.get(id, None)
                            logger.debug("%s(%s)->%s(%s)=%s" % (dut_port, _Sta, dev_port, id, tag))
                            return tag, id, info
        return None, "", {}
    except Exception as e:
        logger.error(str(e))
        return None, str(e), {}


def get_bind_rec(dev_id_dict, dut_port, tagid):
    try:
        _Sta = dev_id_dict.get('DutSta', {}).get(dut_port, "")
        group_name = tagid_groupname.get(tagid, "")
        if _Sta and group_name:
            for retry in range(3):
                dev_now, _local = scan_audio(dev_id_dict)
                for id, info in dev_id_dict.items():
                    if "VID" in id and id in dev_now:
                        if info.get("Sta", "") == _Sta and info.get("GroupName", "") == group_name:
                            dev_port = info.get("Port", "")
                            tag = dev_now.get(id, None)
                            logger.debug("%s(%s)->%s(%s)=%s" % (dut_port, _Sta, dev_port, id, info.get("Name", "")))
                            return tag, id, info
        return None, "", {}
    except Exception as e:
        logger.error(str(e))
        return None, str(e), {}


def get_wmi_info(groups=["COM", "SCAN", "IR"], filter="COM"):
    info = {}
    wmi = win32com.client.GetObject("winmgmts:")
    # for usb in wmi.InstancesOf("Win32_SerialPort"):  # CHJ Win32_SerialPort 无法罗列 第三方驱动串口
    #     print("设备信息：", usb.DeviceID, usb.Name, usb.PNPDeviceID)
    for usb in wmi.InstancesOf("Win32_PnPEntity"):
        if ("VID_" in usb.DeviceID):
            DevicePath = usb.PNPDeviceID
            _VPid = re.compile(r"VID_\w+&PID_\w+").findall(DevicePath)
            if _VPid:
                _ID = _VPid[0]
                if _ID in bind_id:
                    if bind_id[_ID] in groups:
                        _Name = usb.Name
                        if filter in _Name:
                            # print("设备信息：",bind_id[_ID], usb.DeviceID, usb.Name, usb.PNPDeviceID)
                            info[_Name] = usb.PNPDeviceID
    # print(info)
    return info


def scan_serial(dev_id_dict):
    com_ports = serial.tools.list_ports.comports()
    _local_bind = {}
    bind_com = {}
    _wmi_info = {}
    for port in com_ports:
        if (port.vid):
            vid = "%04X" % port.vid
            pid = "%04X" % port.pid
            vid_pid = "VID_%s&PID_%s" % (vid, pid)
            if vid_pid in bind_id:
                Location = port.location
                DevicePath = "%s %s" % (vid_pid, port.device)
                if not dev_id_dict.get(DevicePath, {}):
                    dev_id_dict[DevicePath] = {}
                dev_id_dict[DevicePath]["ID"] = vid_pid
                _group = bind_id.get(vid_pid, "Error")
                dev_id_dict[DevicePath]["Group"] = _group
                dev_id_dict[DevicePath]["GroupName"] = com_groupname.get(_group, "未知")
                dev_id_dict[DevicePath]["Name"] = port.description
                # dev_id_dict[DevicePath]["Name"] = port.name
                dev_id_dict[DevicePath]["location"] = Location
                dev_id_dict[DevicePath]["COM"] = port.device
                if Location:
                    # _port=Location.split(":")[0].replace("-",".")
                    _port = Location.split(":")[0].split("-")[-1]
                    dev_id_dict[DevicePath]["local"] = _port
                    _local_bind[_port] = DevicePath
                else:
                    if not _wmi_info:
                        _wmi_info = get_wmi_info()  # CHJ 这个很卡？
                    if port.description in _wmi_info:
                        lDevicePath = _wmi_info[port.description]
                        FName, Location = get_campath_reg(lDevicePath)
                        dev_id_dict[DevicePath]["local"] = Location
                        _local_bind[Location] = DevicePath
                bind_com[DevicePath] = port.device
    return bind_com, _local_bind


class Box_DevGroup(tk.Toplevel):
    def __init__(self, master=None, cnf={}, setting={}, result={}, **kw):
        self.setting = setting
        self.result = result
        super().__init__(master, cnf, **kw)
        if ("geometry" in self.setting):
            self.geometry(self.setting["geometry"])
        if ("title" in self.setting):
            self.title(self.setting["title"])
        if ("tip" in self.setting):
            self.tip = self.setting["tip"]
        else:
            self.tip = "Input:"
        self.wm_attributes('-topmost', 1)
        # self.iconbitmap("./ico.ico")
        self.transient(master)  # 调用这个函数就会将Toplevel注册成master的临时窗口,临时窗口简化最大最小按钮
        self.resizable(height=False, width=False)  # 禁止调整大小
        self.grab_set()  # 将此应用程序的所有事件路由到此窗口小部件
        self.init_data()
        if self.cmp_deploy():
            logger.debug(self.dev_id_load)
            self.result["Deploy"] = self.dev_id_load
            self.result["result"] = True
            self.set_rec_volume()  # 保存的时候,设置rec设备的录制音量
            self.after(1, self.destroy)
        else:
            self.init_ui()
            # self.wm_attributes("-alpha",0)
            self.loop_id = None
            self.loop()
    def cmp_deploy(self):
        if not "DutSta" in self.dev_id_load:
            logger.error("CmpDeploy illegal")
            return False
        if not "PortSta" in self.dev_id_load:
            logger.error("CmpDeploy illegal")
            return False
        with usb1.USBContext() as context:
            for device in context.getDeviceList(skip_on_error=True):
                for setting in device.iterSettings():
                    get_inter = (setting.getClass(), setting.getSubClass(), setting.getProtocol())
                    if (get_inter in bind_id):
                        bus = device.getBusNumber()
                        subport = device.getPortNumberList()
                        portpath = [bus] + subport
                        portname = ".".join([str(i) for i in portpath])
                        b_id = bind_id[get_inter]
                        if not portname in self.dev_id_load.get("DutSta",{}):
                            logger.error("CmpDeploy New Dut Port")
                            return False
        cmp_usb_err=listen_usb(self.dev_id_load)  # 检查了port与vpid的对应关系
        if cmp_usb_err:
            logger.error("CmpDeploy NoFound %s"%cmp_usb_err)
            return False
        now_cap,local_now_v=scan_video(self.dev_id_dict)
        now_iid,local_now_a=scan_audio(self.dev_id_dict)
        now_com,local_now_a=scan_serial(self.dev_id_dict)
        load_groups=[]
        for id,_info in self.dev_id_load.items():
            _group=_info.get("Group","")
            if _group:
                load_groups.append(_group)
                if _group in self.rec_cam:
                    if "MI_02" in id:
                        cmp=id in now_iid
                    else:
                        cmp=id in now_cap
                elif _group in com_groupname:
                    cmp=id in now_com
                elif _group in rec_groupname:
                    cmp=id in now_iid
                elif _group in cam_groupname:
                    cmp=id in now_cap
                if not cmp:
                    logger.error("CmpDeploy NoFound %s=%s" % (_group,id))
                    return False
        for g in self.conf_dev_groupid:
            if not g in load_groups:
                logger.error("CmpDeploy NoFound %s" % g)
                return False
        return True
    def init_data(self):
        self.run_once = True  # 仅执行一次标志位
        self.dev_file = "./dev.json"  # 部署保存文件
        self.dev_id_load = self.read_json(self.dev_file)
        # print(self.setting.get("config",{}).get("SETTING",{}))
        self.conf_dev_groupid = self.setting.get("deploy_dev", ["HDMI", "SPDIF"])
        self.conf_sta_total = int(self.setting.get("sta_total", 2))
        self.conf_volumes = self.setting.get("volumes", {})
        self.rec_cam = ["HDMI", "AV"]  # 支持通过音频绑定视频的group(HDMI采集卡差异("&MI_02", "&MI_00")[:-1])
        self.speed3_gname = ["HDMI音频"]  # 需要检测online的设备是否接入USB3.0的GroupName标签(暂未)
        self.dev_id_dict = {}  # 汇总所有的设备id={info}
        self.port_sta = self.dev_id_load.get("PortSta", {})  # 记录绑定工具 PORTNAME -> Sta 空为0
        self.usb_log = []  # 用于记录usb的 PORTNAME 增删
        self.check_show = {}  # 界面标签,用于结果提示

    def dev_dict_filter(self, devdict):
        f_dict = {}
        for id, d in devdict.items():
            if isinstance(d, dict):
                _group = d.get("Group", "")
                if _group:
                    if "Online" in d:
                        if d["Online"] and _group in self.conf_dev_groupid:  # 过滤非配置中设备
                            f_dict[id] = {key: d[key] for key in
                                          d.keys() - {'CapId', "iid", "Online", "SPEED3", "location","local"}}  # 过滤动态变量
                    else:
                        if _group in self.conf_dev_groupid:  # 过滤非配置中设备
                            f_dict[id] = {key: d[key] for key in
                                          d.keys() - {'CapId', "iid", "Online", "SPEED3", "location","local"}}  # 过滤动态变量
                else:
                    f_dict[id] = d
            else:
                f_dict[id] = d
        self.port_sta.update()
        f_dict["PortSta"] = self.port_sta
        f_dict["PortSta"].update(devdict.get("DutSta", {}))
        return f_dict

    def save_json(self, filename):
        save_dict = self.dev_dict_filter(self.dev_id_dict)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(save_dict, f, ensure_ascii=False, indent=4)
        return save_dict

    def read_json(self, filename):
        try:
            if not os.path.exists((filename)):
                print("NoFound 未找到部署文件")
                return {}
            with open(filename, "r", encoding='utf-8') as f:
                json_dict = eval(f.read())
            return json_dict
        except Exception as e:
            print("部署文件异常%s" % e)
            return {}

    def set_rec_volume(self):
        for d in self.dev_id_dict.values():
            iid = d.get("iid", "")
            if iid:
                _name = d.get("Name", "未配置")
                _volume = self.conf_volumes.get(d.get("Group", ""), 80)
                self.set_volume(iid, _name, _volume)

    def set_volume(self, iid, name, value=80):
        try:
            os.popen('SoundVolumeView.exe /SetVolume %s %s' % (iid, value))
            logger.debug("自动设定录音设备%s音量%s" % (name, value))
        except:
            pass

    def b_commit(self):
        deploy = self.save_json(self.dev_file)
        logger.debug(deploy)
        self.result["Deploy"] = deploy
        self.result["result"] = True
        self.set_rec_volume()  # 保存的时候,设置rec设备的录制音量
        if not self.run_once:
            self.after_cancel(self.loop_id)
        self.after(1, self.destroy)  # 解决bad window path name ".!box_devgroup" 问题
        # self.destroy()

    def scan_usb(self):
        # usb_speed = {0x0100: "USB_SPEED_LOW", 0x0110: "USB_SPEED_FULL", 0x0200: "USB_SPEED_HIGH",
        #              0x0250: "USB_SPEED_WIRELESS", 0x0300: "USB_SPEED_SUPER", 0x0310: "USB_SPEED_SUPER_PLUS"}
        #   USB_SPEED_LOW, USB_SPEED_FULL,        /* usb 1.1 */
        #   USB_SPEED_HIGH,                /* usb 2.0 */
        #   USB_SPEED_WIRELESS,            /* wireless (usb 2.5) */
        #   USB_SPEED_SUPER,            /* usb 3.0 */
        #   USB_SPEED_SUPER_PLUS            /* usb 3.1 */
        busb_info = {}
        port_log = []
        port_vpid_dev={}
        for c in bind_id.values():
            busb_info[c] = []
        with usb1.USBContext() as context:
            for device in context.getDeviceList(skip_on_error=True):
                vid = "%04X" % device.getVendorID()
                pid = "%04X" % device.getProductID()
                vid_pid = "VID_%s&PID_%s" % (vid, pid)
                bus = device.getBusNumber()
                subport = device.getPortNumberList()
                portpath = [bus] + subport
                portname = ".".join([str(i) for i in portpath])
                bcd = device.getbcdUSB()  # usb_speed.get(bcd,"Unknown")
                is_usb3 = bcd >= 0x0300  # device.getDeviceSpeed()
                info = {"PORTNAME": portname, "PORTPATH": portpath, "ADDRESS": device.getDeviceAddress(),
                        "BUS": bus, "VID": vid, "PID": pid, "ID": vid_pid, "SUBPORT": subport, "SPEED3": is_usb3}
                if (vid_pid in bind_id):
                    b_id = bind_id[vid_pid]
                    busb_info[b_id].append(info)
                    port_log.append(portname)
                    port_vpid_dev[portname]= {"ID": vid_pid,"SPEED3": is_usb3,"Group":b_id}
                else:
                    for setting in device.iterSettings():
                        get_inter = (setting.getClass(), setting.getSubClass(), setting.getProtocol())
                        if (get_inter in bind_id):
                            b_id = bind_id[get_inter]
                            busb_info[b_id].append(info)
                            port_log.append(portname)
                            break
        usb_change, add_usb, del_usb = self.get_diff(port_log)
        add_dev={}
        del_dev={}
        if usb_change:
            for a in add_usb:
                _dev=port_vpid_dev.get(a,"")
                if _dev:add_dev[a]=_dev
                self.dev_show.set("设备信息 (新增%s)" % a)
            for d in del_usb:
                _dev=port_vpid_dev.get(d,"")
                if _dev:del_dev[d]=_dev
                self.dev_show.set("设备信息 (移除%s)" % d)
        return busb_info, usb_change, add_dev, del_dev

    def get_diff(self, usbnow):
        _same = set(self.usb_log).intersection(set(usbnow))
        _add = list(set(usbnow).difference(_same))
        _del = list(set(self.usb_log).difference(_same))
        has_change = _add or _del
        if has_change:
            self.usb_log = usbnow
            # print("=",_add,_del)
        return has_change, _add, _del

    def bind_updata(self, busb_info, change_once, reg_busb):
        for i, f in busb_info.items():
            if i in self.bind_var:
                _infolist = busb_info.get(i, [])
                _blist = self.bind_var.get(i, [])
                if i == "DUT":  # 特殊处理DUT,可手动输入的
                    # print(i,_blist,self.port_sta)
                    auto_adb = [i.get("PORTNAME", "Error") for i in _infolist]
                    # print(auto_adb)
                    empty_blist = []
                    used_blist = []
                    write_blist = []
                    for j, b in enumerate(_blist):
                        _br, _bu, _bt, _df = b
                        _bu_str = _bu.get().strip()
                        if _bu_str == "":
                            empty_blist.append(b)
                        else:
                            if _bu_str in auto_adb:
                                auto_adb.remove(_bu_str)
                                used_blist.append(b)
                                _bt.set("%s(在线)" % _df)
                                # print("在线", self.port_sta.get(_bu_str, 0), change_once, _br.get())
                                if change_once:
                                    _br.set(self.port_sta.get(_bu_str, 0))  # 从绑定数据port_sta中读取
                                _bu.set(_bu_str)
                                _sta = _br.get()
                                if _sta:
                                    self.port_sta[_bu_str] = _sta
                            else:
                                if _bt.get() == _df:
                                    write_blist.insert(0, b)
                                else:
                                    _bt.set("%s(离线)" % _df)
                                    write_blist.append(b)
                    if auto_adb:
                        for b in empty_blist:
                            _br, _bu, _bt, _df = b
                            _bu_str = auto_adb.pop()
                            _bu.set(_bu_str)
                            used_blist.append(b)
                            _bt.set("%s(新增)" % _df)
                            if change_once:
                                _br.set(self.port_sta.get(_bu_str, 0))  # 从绑定数据port_sta中读取
                            _bu.set(_bu_str)
                            _sta = _br.get()
                            if _sta:
                                self.port_sta[_bu_str] = _sta
                            if not auto_adb: break
                    if auto_adb:
                        for b in write_blist:
                            _br, _bu, _bt, _df = b
                            _bu_str = auto_adb.pop()
                            _bu.set(_bu_str)
                            used_blist.append(b)
                            _bt.set("%s(强制新增)" % _df)
                            if change_once:
                                _br.set(self.port_sta.get(_bu_str, 0))  # 从绑定数据port_sta中读取
                            _bu.set(_bu_str)
                            _sta = _br.get()
                            if _sta:
                                self.port_sta[_bu_str] = _sta
                            if not auto_adb: break
                    if auto_adb:
                        mbox.showwarning("警告 Warning", "在线DUT与工位数量不匹配", parent=self)
                else:
                    for j, b in enumerate(_blist):
                        _br, _bu, _bt, _df = b
                        if j < len(_infolist):
                            _port = _infolist[j].get("PORTNAME", "Error")
                            if change_once:
                                _br.set(self.port_sta.get(_port, 0))  # 从绑定数据port_sta中读取
                            _bu.set(_port)
                            self.port_sta[_port] = _br.get()
                            for id, _info in self.dev_id_dict.items():
                                if i == _info.get("Group", ""):
                                    if _port == _info.get("Port", ""):
                                        _sta_v = _br.get()
                                        if _sta_v == _info.get("Sta", ""):
                                            if i in self.rec_cam:
                                                if "MI_02" in id:
                                                    self.bind_cam(id, _port, _sta_v)
                                                    self.dev_id_dict[id]["SPEED3"] = _infolist[j].get("SPEED3", False)
                                                    _tip = "[%s]%s" % (
                                                    _info.get("GroupName", ""), _info.get("Name", ""))
                                                    _bt.set(_tip)
                                            else:
                                                self.dev_id_dict[id]["SPEED3"] = _infolist[j].get("SPEED3", False)
                                                _tip = "[%s]%s" % (_info.get("GroupName", ""), _info.get("Name", ""))
                                                _bt.set(_tip)
                        else:
                            _br.set(0)
                            _bu.set("")
                            _bt.set(_df)

    def bind_check(self):
        sta_check = [len(self.conf_dev_groupid) + 1] * self.conf_sta_total
        show_err = []
        dut_bind = {}
        on_line = {}
        for n, l in self.bind_var.items():
            if n == "DUT":
                _log = []
                _log_sta = []
                for b in l:
                    _usbp = b[1].get()
                    if _usbp:
                        if _usbp in _log:
                            show_err.append("DUT绑定USB端口重复%s" % _usbp)
                        else:
                            _log.append(_usbp)
                    _sta_v = b[0].get()  # _br, _bu, _bt, _df = b
                    if _sta_v:
                        _ind = _sta_v - 1
                        if _ind < len(sta_check):
                            sta_check[_ind] -= 1
                            if _ind in _log_sta:
                                show_err.append("%s设备绑定工站%s重复" % (n, _sta_v))
                            else:
                                _log_sta.append(_ind)
                            dut_bind[_usbp] = _sta_v
            else:
                _log_sta = []
                for b in l:
                    _sta_v = b[0].get()  # _br, _bu, _bt, _df = b
                    _on_port = b[1].get()
                    if _sta_v:
                        on_line[_on_port] = n
                        _ind = _sta_v - 1
                        if _ind < len(sta_check):
                            sta_check[_ind] -= 1
                            if _ind in _log_sta:
                                show_err.append("%s设备绑定工站%s重复" % (n, _sta_v))
                            else:
                                _log_sta.append(_ind)
                        if (not self.run_once) and b[2].get()==b[3]:
                            show_err.append("%s未适配"%b[3])
        for u, s in dut_bind.items():
            if not (u and self.isusbport(u)):
                show_err.append("工站%s未配置DUT端口" % s)
        for i, v in enumerate(sta_check):
            if v == 0:
                col = "green"
            else:
                col = "red"
                show_err.append("工站配置未完成")
            show = self.check_show.get("label%d" % i, None)
            show["background"] = col
        # Online + SPEED3
        for gv in self.dev_id_dict.values():
            gv["Online"] = False  # 动态Online标签设定
            g_group = gv.get("Group", "")
            g_port = gv.get("Port", "")
            if g_port in on_line and on_line[g_port] == g_group:
                gv["Online"] = True  # 更新Online
                if gv.get("GroupName", "") in self.speed3_gname:  # SPEED3
                    g_sta = gv.get("Sta", "")
                    if g_sta:
                        g_speed3 = gv.get("SPEED3", False)
                        if not g_speed3:
                            show_err.append("工站%s(%s)%s未接入USB3.0" % (g_sta, g_port, groudid_name.get(g_group, "")))
        if show_err:
            show_msg = ";".join(list(set(show_err)))
            self.show_msg["text"] = show_msg
            self.show_msg["background"] = "#f52536"
            self.bsave["state"] = "disabled"
        else:
            self.dev_id_dict["DutSta"] = dut_bind
            self.show_msg["text"] = "配置通过"
            self.show_msg["background"] = "green"
            self.bsave["state"] = "enable"
            return True
        return False

    def isusbport(self, usb):
        if "." in usb:
            port = usb.split(".")
            for p in port:
                if not p.isdigit():
                    return False
            return True
        return False

    def bind_cam(self, DevicePath, usbport, sta):
        _group = self.dev_id_dict.get(DevicePath, {}).get("Group")
        if _group in self.rec_cam:
            camDevicePath = DevicePath.replace("&MI_02", "&MI_00")[:-1] + "0"
            if self.dev_id_dict.get(camDevicePath, {}):
                self.dev_id_dict[camDevicePath]["Port"] = usbport
                if sta:
                    self.dev_id_dict[camDevicePath]["Sta"] = sta

    def get_match_port(self, port, busb, usbinfo):
        match = []
        for u, r in busb.items():
            _mlen = -len(u) - 1
            # print(port[_mlen:],u,r)
            if port[_mlen:] == "." + u:
                if (usbinfo.get("ID", "") == self.dev_id_dict.get(r, {}).get("ID", "")):  # 复查 VPID
                    match.append(r)
        if len(match) == 1:
            return True, match[0]
        return False, match

    def loop(self):
        try:
            now_com, com_local_bind = scan_serial(self.dev_id_dict)
            now_cap, cam_local_bind = scan_video(self.dev_id_dict)
            now_iid, rec_local_bind = scan_audio(self.dev_id_dict)
            _infodict, _change, add_dev, del_dev = self.scan_usb()
            self.bind_updata(_infodict, _change, {})
            _check = self.bind_check()

            if self.run_once:  # 首次执行并设备不变更
                _once_dict = self.dev_dict_filter(self.dev_id_dict)
                # print(_check,_once_dict)
                # print(self.dev_id_load)
                if _check and self.dev_id_load == _once_dict:
                    self.b_commit()
                    return
                self.guide_once()   # 执行部署向导
                self.run_once = False
            # print(self.port_sta)
            # print(self.dev_id_dict)
            # print()
            self.loop_id = self.after(200, self.loop)
        except Exception as e:
            print(traceback.print_exc())
            print(e)
    def guide_reset(self):
        self.run_once=True
    def guide_once(self):
        self.bsave["state"] = "disabled"
        self.breset["state"] = "disabled"
        g_title="部署向导"
        g_help=["移除需部署的所有设备,然后点击确认"]
        g_help+=["流程%s/%s:\n接入工站Sta%s的所有设备,然后点击确认"%(j+1,self.conf_sta_total,j+1) for j in range(self.conf_sta_total)]
        for i,h in enumerate(g_help):
            ret=mbox.showinfo(g_title,h,parent=self)
            _det_num=(len(self.bind_var)-1)
            for retry in range(3):
                time.sleep(1)
                if i:
                    now_com, com_local_bind = scan_serial(self.dev_id_dict)
                    now_cap, cam_local_bind = scan_video(self.dev_id_dict)
                    now_iid, rec_local_bind = scan_audio(self.dev_id_dict)
                    _infodict, _change, add_dev, del_dev = self.scan_usb()
                    for _port,_uinfo in add_dev.items():
                        self.port_sta[_port]=i
                        _ugroup=_uinfo.get("Group","")
                        _uspeed=_uinfo.get("SPEED3","")
                        _uvpid=_uinfo.get("ID","")
                        for id,_info in self.dev_id_dict.items():
                            if not _info.get("Sta",""):
                                if _info.get("ID", "")==_uvpid and _info.get("Group", "")==_ugroup:
                                    if not (_ugroup in self.rec_cam and "MI_00" in id):  # 过滤集成卡视频
                                        ui_list=self.bind_var.get(_ugroup,[])
                                        if ui_list:
                                            _br, _bu, _bt, _df = ui_list[i-1]
                                            _br.set(i)
                                            _bu.set(_port)
                                            _tip = "[%s]%s" % (_info.get("GroupName", ""), _info.get("Name", ""))
                                            _bt.set(_tip)
                                            _det_num-=1
                                            self.bind_cam(id, _port, i)
                                            self.dev_id_dict[id]["Port"] = _port
                                            self.dev_id_dict[id]["SPEED3"] = _uspeed
                                            self.dev_id_dict[id]["Sta"] = i
                                            now_com, com_local_bind = scan_serial(self.dev_id_dict)
                                            now_cap, cam_local_bind = scan_video(self.dev_id_dict)
                                            now_iid, rec_local_bind = scan_audio(self.dev_id_dict)
                                            break
                else:
                    _infodict, _change, add_dev, del_dev = self.scan_usb()
                    self.port_sta={}
                    self.dev_id_dict={}
                    # print(self.bind_var)
                    for n, l in self.bind_var.items():
                        if not n == "DUT":
                            for b in l:
                                _br, _bu, _bt, _df = b
                                _br.set(0)
                                _bu.set("")
                                _bt.set(_df)
                    if not _change:
                        _det_num=0  # 没有USB变动的情况下,退出移除
                if _det_num:
                    time.sleep(1)
                else:
                    break
            # print(self.scan_usb())
        self.breset["state"] = "enable"
    def init_ui(self):
        self.ui = tk.Frame(self)
        self.ui.pack(fill=tk.BOTH, expand=1)
        self.columnconfigure(0, weight=1)
        self.bind_var = {}
        self.dev_show = tk.StringVar(value="设备信息")
        for t in range(self.conf_sta_total + 1):
            if t:
                stal = tk.Label(self.ui, text="工站%s" % t, font=('Microsoft YaHei', 12), background="#e9e9e9")
                stal.grid(padx=2, pady=2, sticky=tk.EW, row=0, column=t)
                self.check_show["label%s" % (t - 1)] = stal
            else:
                tk.Label(self.ui, text="USB端口", font=('Microsoft YaHei', 12), background="#e0e0e0").grid(padx=2, pady=2,
                                                                                                         sticky=tk.EW,
                                                                                                         row=0,
                                                                                                         column=t)
        tk.Label(self.ui, textvariable=self.dev_show, font=('Microsoft YaHei', 12), background="#e9e9e9").grid(padx=2,
                                                                                                               pady=2,
                                                                                                               sticky=tk.EW,
                                                                                                               row=0,
                                                                                                               column=t + 1)
        gr = 1
        # DUT组
        _bind_var = []
        for i in range(self.conf_sta_total):
            _bradio = tk.IntVar()
            _busb = tk.StringVar()
            _df = "待测设备DUT%s" % i
            _btips = tk.StringVar(value=_df)
            _bind_var.append((_bradio, _busb, _btips, _df))
            gr += i
            for j in range(self.conf_sta_total + 1):
                if j:
                    tk.Radiobutton(self.ui, text="Sta%s" % j, value=j, variable=_bradio, background="#e9e9e9").grid(
                        padx=2, pady=2, sticky=tk.EW, row=gr, column=j)
                else:
                    tk.Entry(self.ui, textvariable=_busb, font=('Microsoft YaHei', 12), width=10).grid(padx=2, pady=2,
                                                                                                       sticky=tk.EW,
                                                                                                       row=gr,
                                                                                                       column=j)
            tk.Label(self.ui, textvariable=_btips, anchor="nw", font=('Microsoft YaHei', 12),
                     background="#e0e0e0").grid(padx=2, pady=2,
                                                sticky=tk.EW, row=gr,
                                                column=j + 1)
        # 载入DUT
        load_dut = self.dev_id_load.get("DutSta", {})
        if load_dut:
            for i, b in enumerate(_bind_var):
                if i < len(load_dut):
                    # print(load_dut, load_dut.keys(), load_dut.values())
                    b[1].set(list(load_dut.keys())[i])
                    b[0].set(list(load_dut.values())[i])
                    b[2].set("读取配置DUT%s" % i)
        self.bind_var["DUT"] = _bind_var
        for c, gid in enumerate(self.conf_dev_groupid):
            gname = groudid_name.get(gid, "未定义")
            if c % 2:
                gr = self.init_ui_group(gr, groupid=gid, groupname=gname)
            else:
                gr = self.init_ui_group(gr, groupid=gid, groupname=gname, color=["#d5ebe1", "#dbebe4"])
        # 底部
        button_group = ttk.Frame(self.ui)
        self.show_msg = tk.Label(button_group, text="状态信息", background="#e9e9e9")
        self.show_msg.pack(side="left", padx=2, expand=1, fill=tk.X)
        # ttk.Button(button_group, text='Cancel', command=self.destroy).pack(side="right", padx=5)
        self.breset=ttk.Button(button_group, text='重新部署', command=self.guide_reset)
        self.breset.pack(side="right", padx=5)
        self.bsave = ttk.Button(button_group, text='完成', command=self.b_commit, state="disabled")
        self.bsave.pack(side="right", padx=5)
        button_group.grid(padx=2, pady=2, sticky=tk.EW, row=gr + 1, columnspan=6)

    def init_ui_group(self, gr=0, groupid="gid", groupname="Group", color=["#e9e9e9", "#e0e0e0"]):
        # HDMI组
        _bind_var = []
        gr += 1
        for i in range(self.conf_sta_total):
            _bradio = tk.IntVar()
            _busb = tk.StringVar()
            _df = "%s%s" % (groupname, i)
            _btips = tk.StringVar(value=_df)
            gr += i
            for j in range(self.conf_sta_total + 1):
                if j:
                    tk.Radiobutton(self.ui, text="Sta%s" % j, value=j, variable=_bradio,state="disable",
                                   background=color[-1]).grid(padx=2, pady=2, sticky=tk.EW, row=gr, column=j)
                else:
                    tk.Label(self.ui, textvariable=_busb, font=('Microsoft YaHei', 12), background=color[0]).grid(
                        padx=2,
                        pady=2,
                        sticky=tk.EW,
                        row=gr,
                        column=j)
            tk.Label(self.ui, textvariable=_btips, anchor="nw", font=('Microsoft YaHei', 12),
                     background=color[-1]).grid(padx=2,
                                                pady=2,
                                                sticky=tk.EW,
                                                row=gr,
                                                column=j + 1)
            _bind_var.append((_bradio, _busb, _btips, _df))
        self.bind_var[groupid] = _bind_var
        return gr


if __name__ == '__main__':
    print(listen_usb())
    print()
    # root = tk.Tk()
    # setting = {"deploy_dev": ["HDMI", "SPDIF", "LED", "SCAN", "IR", "COM"], "sta_total": 2}
    # box=Box_DevGroup(root, setting=setting)
    # root.wait_window(box)
