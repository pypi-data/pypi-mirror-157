# def click_success():
#     print("haq")
#
# def convert(ui):
#     input=ui.textEdit.toPlainText()
#     ui.textEdit_2.setPlainText(str(input))

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
