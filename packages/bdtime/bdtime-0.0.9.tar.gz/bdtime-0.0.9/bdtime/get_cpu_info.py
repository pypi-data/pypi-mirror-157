import psutil
import platform
import subprocess
from .utils import show_json


def get_cpu_info():
    cpuTimes = psutil.cpu_times()

    # 获取CPU信息中的内存信息
    def memoryInfo(memory):
        return {
            '总内存(total)': str(round((float(memory.total) / 1024 / 1024 / 1024), 2)) + "G",
            '已使用(used)': str(round((float(memory.used) / 1024 / 1024 / 1024), 2)) + "G",
            '空闲(free)': str(round((float(memory.free) / 1024 / 1024 / 1024), 2)) + "G",
            '使用率(percent)': str(memory.percent) + '%',
            # '可用(available)': (memory.available) if hasattr(memory, 'available') else '',
            # '活跃(active)': (memory.active) if hasattr(memory, 'active') else '',
            # '非活跃(inactive)': (memory.inactive) if hasattr(memory, 'inactive') else '',
            # '内核使用(wired)': (memory.wired) if hasattr(memory, 'wired') else ''
        }

    return {
        'CPU型号': get_cpu_version(),
        '物理CPU个数': psutil.cpu_count(logical=False),
        '逻辑CPU个数': psutil.cpu_count(),
        'CPU使用情况': psutil.cpu_percent(percpu=True),
        '虚拟内存': memoryInfo(psutil.virtual_memory()),
        '交换内存': memoryInfo(psutil.swap_memory()),
        '系统启动到当前时刻': {
            pro: getattr(cpuTimes, pro) for pro in dir(cpuTimes) if pro[0:1] != '_' and pro not in ('index', 'count')
        },
    }


# --- CPU型号信息
def get_cpu_version():
    # ret_key = "CPU型号"
    if platform.system() == "Windows":
        # ret = {
        #     # 'CPU生产商': platform.machine(),
        #     ret_key: platform.processor(),
        # }
        ret = platform.processor()
    else:
        # --- cpu型号
        cmd = 'cat /proc/cpuinfo | grep "model name" | uniq'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, encoding='utf-8')
        text = p.communicate()[0]
        cpu_version = text.split(":")[-1].strip()       # cpu型号

        # # --- 生产厂商
        # cmd = 'cat /proc/cpuinfo | grep "vendor_id" | uniq'
        # p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
        # text = p.communicate()[0]
        # cpu_producer = text.split(":")[-1].strip()  # cpu型号
        # ret = {
        #     # 'CPU生产商': cpu_producer,
        #     ret_key: cpu_version,
        # }
        ret = cpu_version
    return ret


def main():
    computer_info = get_cpu_info()

    # --- 剔除不需要的信息
    pop_ls = [
        "CPU使用情况",
        "系统启动到当前时刻",
        "交换内存",
    ]
    for key in pop_ls:
        computer_info.pop(key)

    print("\n\n-------------- CPU信息 -------------\n\n")
    show_json(computer_info)


if __name__ == '__main__':
    main()
