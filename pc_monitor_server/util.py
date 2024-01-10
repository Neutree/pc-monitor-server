import psutil
import platform
import time
import pynvml
import threading
# if platform.system() == "Windows":
#     from win32com.client import GetObject
#     import wmi
#     try:
#         open_hardware_monitor = wmi.WMI(namespace="root/OpenHardwareMonitor")
#     except Exception:
#         print("OpenHardwareMonitor not found, please install it first from https://openhardwaremonitor.org/downloads/")
#         exit(1)
#     wmi_obj = GetObject("winmgmts:\\\\.\\root\\OpenHardwareMonitor")
try:
    pynvml.nvmlInit()
    gpu_count = pynvml.nvmlDeviceGetCount()
except Exception:
    gpu_count = 0

gpu_handles = []
for i in range(gpu_count):
    gpu_handles.append(pynvml.nvmlDeviceGetHandleByIndex(i))

class Util:
    def __init__(self):
        self._last_net_rx = {}
        self._last_net_tx = {}
        self._last_net_time = {}
        self._net_speed_queue_rx = {}
        self._net_speed_queue_tx = {}
        self._net_info = {}
        t = threading.Thread(target=self._update_net_info)
        t.daemon = True
        t.start()

    def get_mem_info(self):
        mem_info = psutil.virtual_memory()
        swap_info = psutil.swap_memory()
        info = {
            "used": mem_info.used,
            "total": mem_info.total,
            "swap_used": swap_info.used,
            "swap_total": swap_info.total
        }
        return info

    def get_cpu_info(self):
        cpu_usage = psutil.cpu_percent()
        info = {
            "usage": [cpu_usage]
        }
        cpu_per_core_usage = psutil.cpu_percent(percpu=True)
        for i, percentage in enumerate(cpu_per_core_usage):
            info["usage"].append(percentage)
        return info

    def get_temp_info(self):
        info = {
            "cpu": []
        }
        if platform.system() == "Windows":
            # cpu_temps = {}
            # # use GetObject
            # ohm_sensor = wmi_obj.InstancesOf('Sensor')
            # for sensor in ohm_sensor:
            #     if sensor.SensorType == "Temperature":
            #         if sensor.Name == "CPU Package":
            #             cpu_temps["package"] = sensor.Value
            #         elif sensor.Name.startswith("CPU Core #"):
            #             cpu_id = int(sensor.Name.split("#")[1])
            #             cpu_temps[cpu_id] = sensor.Value
            # info["cpu"].append(cpu_temps["package"])
            # for i in range(len(cpu_temps) - 1):
            #     info["cpu"].append(cpu_temps[i + 1])
            return info
        temp = psutil.sensors_temperatures()

        for i, t in enumerate(temp["coretemp"]):
            info["cpu"].append(t.current)
        return info

    def get_disk_info(self):
        info = {}
        # list all disk devices
        disk_partitions = psutil.disk_partitions()
        for i, partition in enumerate(disk_partitions):
            if "loop" in partition.device:
                continue
            info[partition.device] = {
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "opts": partition.opts
            }
        return info

    def _update_net_info(self):
        self._net_info = {}
        while True:
            info = {}
            net_io_counters = psutil.net_io_counters(pernic=True)
            for i, net in enumerate(net_io_counters):
                if "lo" in net or "veth" in net or "docker" in net or "br-" in net:
                    continue
                info[net] = {
                    "rx": net_io_counters[net].bytes_sent,
                    "tx": net_io_counters[net].bytes_recv,
                    "pack_tx": net_io_counters[net].packets_sent,
                    "pack_rx": net_io_counters[net].packets_recv,
                    "errin": net_io_counters[net].errin,
                    "errout": net_io_counters[net].errout,
                    "dropin": net_io_counters[net].dropin,
                    "dropout": net_io_counters[net].dropout
                }
                if net not in self._last_net_rx:
                    self._last_net_rx[net] = net_io_counters[net].bytes_recv
                    self._last_net_tx[net] = net_io_counters[net].bytes_sent
                    self._last_net_time[net] = time.time()
                    info[net]["speed_rx"] = 0
                    info[net]["speed_tx"] = 0
                    self._net_speed_queue_rx[net] = []
                    self._net_speed_queue_tx[net] = []
                else:
                    now = time.time()
                    time_diff = now - self._last_net_time[net]
                    if time_diff > 0:
                        speed_rx = (net_io_counters[net].bytes_recv - self._last_net_rx[net]) / time_diff
                        speed_tx = (net_io_counters[net].bytes_sent - self._last_net_tx[net]) / time_diff
                        self._last_net_rx[net] = net_io_counters[net].bytes_recv
                        self._last_net_tx[net] = net_io_counters[net].bytes_sent
                        self._last_net_time[net] = now
                        self._net_speed_queue_rx[net].append(speed_rx)
                        self._net_speed_queue_tx[net].append(speed_tx)
                        if len(self._net_speed_queue_rx[net]) > 10:
                            self._net_speed_queue_rx[net].pop(0)
                            self._net_speed_queue_tx[net].pop(0)
                        info[net]["speed_rx"] = int(sum(self._net_speed_queue_rx[net]) / len(self._net_speed_queue_rx[net]))
                        info[net]["speed_tx"] = int(sum(self._net_speed_queue_tx[net]) / len(self._net_speed_queue_tx[net]))
            self._net_info = info
            time.sleep(0.5)

    def get_net_info(self):
        return self._net_info

    def get_gpu_info(self):
        info = {}
        for i, gpu in enumerate(gpu_handles):
            gpu_info = pynvml.nvmlDeviceGetMemoryInfo(gpu)
            gpu_util = pynvml.nvmlDeviceGetUtilizationRates(gpu)
            gpu_temp = pynvml.nvmlDeviceGetTemperature(gpu, 0)
            gpu_name = pynvml.nvmlDeviceGetName(gpu)
            info[i] = {
                "name": gpu_name.decode("utf-8"),
                "mem_used": gpu_info.used,
                "mem_total": gpu_info.total,
                "gpu_util": gpu_util.gpu,
                "mem_util": gpu_util.memory,
                "temp": gpu_temp
            }
        return info

    def all(self):
        mem = self.get_mem_info()
        cpu = self.get_cpu_info()
        disk = self.get_disk_info()
        net = self.get_net_info()
        gpu = self.get_gpu_info()
        temp = self.get_temp_info()
        info = {
            "mem": mem,
            "cpu": cpu,
            "disk": disk,
            "net": net,
            "gpu": gpu,
            "temp": temp
        }
        return info

