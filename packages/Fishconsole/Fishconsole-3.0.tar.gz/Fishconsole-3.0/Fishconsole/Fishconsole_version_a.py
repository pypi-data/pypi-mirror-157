# def click_success():
#     print("haq")
#
# def convert(ui):
#     input=ui.textEdit.toPlainText()
#     ui.textEdit_2.setPlainText(str(input))

import requests
from Fishconsole import files
import os

if not files.文件存在性检测(r"C:\Fishconsole\img\Fishconsole.png"):
    try:
        os.makedirs(r"C:\Fishconsole\img")
    except FileExistsError:
        pass
    try:
        res=requests.get("https://s2.loli.net/2022/06/30/GTxdluDELZ9tob3.png").content
        with open(r"C:\Fishconsole\img\Fishconsole.png","wb") as f:
            f.write(res)
    except requests.exceptions.ConnectionError:
        pass
    finally:
        pass

def 启动():
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow

    from Fishconsole import Fishconsole_version_b

    from functools import partial  # 传参

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Fishconsole_version_b.Ui_Widget()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
