########################################################################################################################
import os
import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QTextEdit, QPushButton, QMainWindow

from LightControllerThread import LightController
from PyQt5.QtCore import QTime, Qt, QDate
########################################################################################################################
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        title = "Light Controller"
        left = 500
        top = 300
        width = 800
        height = 600
        self.setFixedSize(800,600)
        iconName = "icon.png"
        self.ServerStopFlag = False
        self.ClearDispCount = 0
        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(iconName))
        self.setGeometry(left,  top, width, height)
        self.UiComponents()
        self.show()
      #  self.Text.append("Server Started")
        self.Server_Start()
        ####################################################################################################################
    def UiComponents(self):
        App.aboutToQuit.connect(self.Exit)
        self.Text = QTextEdit(self)
        self.Text.setReadOnly(True)
        self.Text.move(0, 0)
        self.Text.resize(800, 300)
        self.button = QPushButton("Start Server", self)
        self.button.move(150,150)
        self.button.setGeometry(QRect(50,525,200,40))
        self.button1 = QPushButton("Stop Server",self)
        self.button1.move(40,40)
        self.button1.setGeometry(QRect(280,525,200,40))
        self.button2 = QPushButton("Send Command",self)
        self.button2.move(50,50)
        self.button2.setGeometry(QRect(510,525,200,40))
        self.button.clicked.connect(self.Server_Start)
        self.button1.clicked.connect(self.Server_Stop)
        self.button2.clicked.connect(self.LightControl)
        self.button.setEnabled(False)
        self.CurrentLightState = 'OFF'
        self.LightContrlInfo = {
                                'IPAddr' : None,
                                'Channel' : 'Left',
                                'Status' : 'OFF'
                                }
        self.label_IP_Address = QtWidgets.QLabel(self)
        self.label_IP_Address.setText("IP Address")
        self.label_IP_Address.setGeometry(70,320,100,30)

        self.label_Channel = QtWidgets.QLabel(self)
        self.label_Channel.setText("Channel")
        self.label_Channel.setGeometry(270, 320, 100, 30)

        self.label_Status = QtWidgets.QLabel(self)
        self.label_Status.setText("Status")
        self.label_Status.setGeometry(470, 320, 100, 30)

        self.combo_IP_Address = QtWidgets.QComboBox(self)
        self.combo_IP_Address.setGeometry(30, 350, 150, 30)
        self.combo_IP_Address.addItems(["192.168.1.50","192.168.1.51","192.168.1.52","192.168.1.53","192.168.1.54","192.168.1.55","192.168.1.56","192.168.1.57","192.168.1.58","192.168.1.59","192.168.1.60"])

        self.combo_channel = QtWidgets.QComboBox(self)
        self.combo_channel.setGeometry(230, 350, 150, 30)
        self.combo_channel.addItems(["Only Left","Only Right","Both Left & Right"])

        self.combo_status = QtWidgets.QComboBox(self)
        self.combo_status.setGeometry(430, 350, 150, 30)
        self.combo_status.addItems(["ON","OFF"])
    ####################################################################################################################
    def Server_Start(self):
        self.Text.append("Server Started")
        self.button.setEnabled(False)
        self.button1.setEnabled(True)
       # self.Text.append("Server Started")
        self.thread = LightController()
        self.thread.change_value.connect(self.setProgressVal)
        self.thread.StopFlag = False
        self.thread.start()
    ####################################################################################################################
    def Server_Stop(self):
        self.thread.StopFlag = True
        self.button.setEnabled(True)
        self.button1.setEnabled(False)
        self.Text.append("Server Disconnected")
        #self.thread.exit()
        #self.ServerStopFlag = True
    ####################################################################################################################
    def setProgressVal(self, val):
        if(self.ClearDispCount >10):
            self.ClearDispCount = 0
            self.Text.clear()
            self.Text.setText(val)
        else:
            self.Text.append(val)
        self.ClearDispCount = self.ClearDispCount + 1
        #self.Text.setText(val)
       # print(val)
    ####################################################################################################################
    def LightControl(self):
        #self.Text.clear()
        self.thread.LightContrlInfo['IPAddr'] = self.combo_IP_Address.currentText()
        self.thread.LightContrlInfo['Channel'] = self.combo_channel.currentText()
        self.thread.LightContrlInfo['Status'] = self.combo_status.currentText()
        self.thread.LightCntrlFlag = True
    ####################################################################################################################
    def Exit(self):
        self.thread.StopFlag = False
        pass

########################################################################################################################
if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec())
########################################################################################################################
