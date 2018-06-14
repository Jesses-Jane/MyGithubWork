import sys
from PyQt5 import QtCore, QtGui, QtWidgets


# 直接运行程序时的入口
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    # Window系统提供的模式
    model = QtWidgets.QDirModel()
    tree = QtWidgets.QTreeView()
    # 为部件添加模式
    tree.setColumnHidden(0, True)
    # tree.setHeaderHidden(True)

    tree.setModel(model)
    tree.setWindowTitle(tree.tr("Dir View"))
    tree.resize(640, 480)
    tree.show()
    sys.exit(app.exec_())
