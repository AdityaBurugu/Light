import datetime
import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import json
import pandas as pd
from ping3 import ping

from LightControllerThread import LightController
class Time_Set(QDialog):
    def __init__(self):
        super(Time_Set, self).__init__()
        self.setFixedSize(400,300)

        self.setWindowTitle("Shift")


        this_moment = QtCore.QTime.currentTime()

        self.Dict = {"trigger Mode":None,"On Time":None,"Off Time":None}

        self.AutoOff = QRadioButton(self)
        self.AutoOff.setGeometry(50,40,100,30)
        self.AutoOff.setText("Auto")

        self.presenttimehour = datetime.datetime.now().strftime("%H")
        self.presenttimemin = datetime.datetime.now().strftime("%M")
        self.presenttimesec = datetime.datetime.now().strftime("%S")
        self.presenttimep = datetime.datetime.now().strftime("%p")
        print(self.presenttimehour,self.presenttimemin,self.presenttimesec,self.presenttimep)

        self.Shift = QRadioButton(self)
        self.Shift.setGeometry(250, 40, 100, 30)
        self.Shift.setText("Shift")

        self.label_StartTime = QLabel("Start Time",self)
        self.label_StartTime.setGeometry(50,100,100,30)

        self.label_StopTime = QLabel("Stop Time", self)
        self.label_StopTime.setGeometry(250, 100, 100, 30)

        self.starttimeedit = QTimeEdit(self)
        self.starttimeedit.setGeometry(50,150,100,30)
        self.starttimeedit.hide()
        self.starttimeedit.setTime(QTime(int(self.presenttimehour[0:2]),int(self.presenttimemin),int(self.presenttimesec)))

        self.stoptimeedit = QTimeEdit(self)
        self.stoptimeedit.setGeometry(250, 150, 100, 30)
        self.stoptimeedit.hide()
        self.stoptimeedit.setTime(QTime.currentTime().addSecs(300))

        self.setbutton = QPushButton("SET",self)
        self.setbutton.setGeometry(150,230,100,30)
        self.setbutton.clicked.connect(self.set)
        self.setbutton.hide()

        self.group = QButtonGroup(self)
        self.group.addButton(self.AutoOff)
        self.group.addButton(self.Shift)

        self.Shift.clicked.connect(self.Window)
        self.AutoOff.clicked.connect(self.Window2)
        with open('Time.json') as f:
            ServerConfigDict = json.load(f)
        if ServerConfigDict["trigger Mode"]=="Auto":
            self.AutoOff.click()
            self.stoptimeedit.hide()
            self.starttimeedit.hide()
            self.label_StopTime.hide()
            self.label_StartTime.hide()
            self.setbutton.hide()
        else:
            self.Shift.click()
            self.stoptimeedit.show()
            self.starttimeedit.show()
            self.label_StartTime.show()
            self.label_StopTime.show()

    def set(self):
        self.Dict["trigger Mode"] = "Shift"
        if int(self.starttimeedit.time().hour())>12:
            if int(self.starttimeedit.time().minute())<10:
                self.Dict["On Time"] = str(self.starttimeedit.time().hour()) + ':0' + str(self.starttimeedit.time().minute()) + ' ' +"PM"
            else:
                self.Dict["On Time"] = str(self.starttimeedit.time().hour()) + ':' + str(self.starttimeedit.time().minute()) + ' ' + "PM"
        else:
            if int(self.starttimeedit.time().minute())<10:
                self.Dict["On Time"] = str(self.starttimeedit.time().hour()) + ':0' + str(self.starttimeedit.time().minute()) + ' ' +"AM"
            else:
                self.Dict["On Time"] = str(self.starttimeedit.time().hour()) + ':' + str(self.starttimeedit.time().minute()) + ' ' + "AM"

        if int(self.stoptimeedit.time().hour())>12:
            if int(self.stoptimeedit.time().minute())<10:
                self.Dict["Off Time"] = str(self.stoptimeedit.time().hour()) + ':0' + str(self.stoptimeedit.time().minute()) + ' ' +"PM"
            else:
                self.Dict["Off Time"] = str(self.stoptimeedit.time().hour()) + ':' + str(self.stoptimeedit.time().minute()) + ' ' + "PM"
        else:
            if int(self.stoptimeedit.time().minute())<10:
                self.Dict["Off Time"] = str(self.stoptimeedit.time().hour()) + ':0' + str(self.stoptimeedit.time().minute()) + ' ' +"AM"
            else:
                self.Dict["Off Time"] = str(self.stoptimeedit.time().hour()) + ':' + str(self.stoptimeedit.time().minute()) + ' ' + "AM"


        with open('Time.json', 'w') as json_file:
            json.dump(self.Dict, json_file)
    def Window(self):
        self.stoptimeedit.show()
        self.starttimeedit.show()
        self.label_StopTime.show()
        self.label_StartTime.show()
        self.setbutton.show()
        print("Shift")
    def Window2(self):
        self.stoptimeedit.hide()
        self.starttimeedit.hide()
        self.label_StartTime.hide()
        self.label_StopTime.hide()
        self.setbutton.hide()
        self.Dict["trigger Mode"] = "Auto"
        self.Dict["On Time"] = ""
        self.Dict["Off Time"] = ""
        with open('Time.json', 'w') as json_file:
            json.dump(self.Dict, json_file)
        print("Auto")

class Soft_Panel_Gui(QMainWindow):
    def __init__(self):
        super(Soft_Panel_Gui, self).__init__()
        self.setFixedSize(1920,990)
        self.move(0,0)
        self.setWindowTitle("Light Controller")

        self.button = QAction("Start Server", self)
        self.button.setIcon(QIcon("Resources/startserver.png"))
        self.button1 = QAction("Stop Server", self)
        self.button1.setIcon(QIcon("Resources/StopServer.png"))
        self.settings = QAction(self)
        self.settings.setIcon(QIcon("Resources/Settings-icon.png"))
        self.button.triggered.connect(self.Server_Start)
        self.button1.triggered.connect(self.Server_Stop)
        self.settings.triggered.connect(self.TimerSetter)
        self.button.setEnabled(False)
        self.CurrentLightState = 'OFF'
        self.LightContrlInfo = {
            'IPAddr': None,
            'Channel': 'Left',
            'Status': 'OFF'
        }

        self.label_Image = QtWidgets.QLabel(self)
        self.label_Image.setGeometry(QtCore.QRect(0, 0, 1920, 990))
        self.pixmap = QPixmap('Site_Info/SoftPanel.jpg')
        self.label_Image.setPixmap(self.pixmap)

        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QtCore.QSize(56, 35))
        self.toolbar.setStyleSheet("background-color : transparent")
        self.toolbar.addAction(self.button)
        self.toolbar.addAction(self.button1)
        self.toolbar.addAction(self.settings)
        self.addToolBar(self.toolbar)

        self.CentralButton= QPushButton(self)
        self.CentralButton.setText("Central")
        self.CentralButton.setGeometry(850,500,300,30)

        self.Server_Start()

        self.timer=QtCore.QTimer(self)
        self.timer.start(600000)
        self.timer.timeout.connect(self.timeout)

        hubpath = "LightPosition.csv"

        with open('LightConfig.JSON') as f:
            ServerConfigDict = json.load(f)
            print(ServerConfigDict)

        try:
            self.LightPositions = pd.read_csv("Site_Info/LightPosition.csv")
            self.CBoxList = []
            self.HubIPAddr = []
            for i in range(len(self.LightPositions)):
                CBox = QCheckBox(self)
                self.CBoxList.append(CBox)
                self.CBoxList[i].setStyleSheet("QCheckBox"
                                               "{"
                                               "padding : 5px;"
                                               "}"
                                               "QCheckBox::indicator"
                                               "{"
                                               "border : 2px solid white;"
                                               "background-color : rgb(255, 255, 255);"
                                               "width : 20px;"
                                               "height : 20px;"
                                               "border-radius :12px;"
                                               "}")
                self.CBoxList[i].setToolTip(str(self.LightPositions['LightID'].iloc[i]))
                self.HubIPAddr.append(str(self.LightPositions['LightIP'].iloc[i]))

                self.CBoxList[i].setGeometry(
                    QtCore.QRect(self.LightPositions['X'].iloc[i], self.LightPositions['Y'].iloc[i],
                                 self.LightPositions['W'].iloc[i],
                                 self.LightPositions['H'].iloc[i]))
        except:
            print(hubpath + ' is missing')
            QtWidgets.QMessageBox.critical(self, hubpath + " File Missing?",
                                           f'''{hubpath[10:-4]}.aes File is not found in\n{os.getcwd()}\ {"Site_Info"}''')
            exit(0)

    def timeout(self):
        print("timeout")

    def Server_Start(self):
        self.button.setEnabled(False)
        self.button1.setEnabled(True)
        # self.Text.append("Server Started")
        self.thread = LightController()
        self.thread.StopFlag = False
        self.thread.start()

    ####################################################################################################################
    def Server_Stop(self):
        self.thread.StopFlag = True
        self.button.setEnabled(True)
        self.button1.setEnabled(False)
        # self.thread.exit()
        # self.ServerStopFlag = True

    ####################################################################################################################
    def TimerSetter(self):
        self.LightTimer = Time_Set()
        self.LightTimer.show()
    ####################################################################################################################
    def LightControl(self):
        # self.Text.clear()
        self.thread.LightContrlInfo['IPAddr'] = self.combo_IP_Address.currentText()
        self.thread.LightContrlInfo['Channel'] = self.combo_channel.currentText()
        self.thread.LightContrlInfo['Status'] = self.combo_status.currentText()
        self.thread.LightCntrlFlag = True

    ####################################################################################################################
    def Exit(self):
        self.thread.StopFlag = False
        pass

if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Soft_Panel_Gui()
    window.show()
    sys.exit(App.exec())