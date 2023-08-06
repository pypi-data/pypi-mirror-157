"""
这是Fishconsole Project的后台安装模块，无需调用，因为根本就没有函数，他的存在仅仅只是为了缓解我看Fishsys的压力罢了

----

"""


import os

exe = '''

import time

try:
    from Fishconsole import *

except ImportError:
    import os

    os.system("pip install Fishconsole")
import os
import requests


pid = files.缓存(2, 变量名="lastpid")

if pid=="error":
    files.缓存(1,数据={'lastpid':12345})


try:
    os.kill(pid, 0)
    上一个进程 = True
except:
    上一个进程 = False
if not 上一个进程:
    自己的pid = os.getpid()
    print(logs.日志("上一个进程已死"))
    files.缓存(3, 数据={'lastpid': 自己的pid})
else:
    logs.安全退出("上一个进程不存在")
    exit()



print(logs.日志("Fishconsole Project资源文件保护后台启动","绿色"))
while True:

    try:
        Fishconsole_logo = open("C:\Fishconsole\img\Fishconsole.png", "rb")
        Fishconsole_logo.read()
    except:
        print("文件未找到，程序将会自动下载")
        try:
            res = requests.get("https://s2.loli.net/2022/06/30/GTxdluDELZ9tob3.png").content
            with open("C:\Fishconsole\img\Fishconsole.png", "wb+") as Fishconsole_logo:
                Fishconsole_logo.write(res)
        except:
            pass



    Fishconsole_fcc = open("Fishconsole.fcc", "rb")
    Fishconsole_fcc.read()

    File_Protect = open("C:\Fishconsole\programes\FileProtect\File_Protect.py", "rb")
    File_Protect.read()

    time.sleep(20) #没必要使用input开假循环，因为有可能你的文件会因为网络的原因没有被下下来，如果没有被下下来就循环，下下来就不管，毕竟现在看起来也没怎么耗后台

'''

start = """

cd C:\Fishconsole\programes\FileProtect
dir

deactivate
rem 尝试退出虚拟环境
if %errorlevel% == 0 ( echo successfully ) else ( goto loop)
:loop

start pythonw  C:\Fishconsole\programes\FileProtect\File_Protect.py




"""

os.makedirs('C:\Fishconsole\programes\FileProtect', exist_ok=True)
with open("C:\Fishconsole\programes\FileProtect\File_Protect.py", "w", encoding="utf-8") as f:
    f.write(exe)
    f.close()


用户名=os.getenv('username')

with open(f"C:/Users/{用户名}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/File_Protect_start.bat", "w", encoding="ANSI") as f:
    f.write(start)
    f.close()



