########################################################################################################################
import csv
import datetime
import json
import os
import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import QRect, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTextEdit, QPushButton, QMainWindow, QToolBar, QAction, QDialog, QRadioButton, QLabel, \
    QTimeEdit, QButtonGroup, QLineEdit, QMessageBox, QTableWidget, QFileDialog, QHeaderView, QTableWidgetItem
import pandas as pd
import IP_Vallidator
from LightControllerThread import LightController
from PyQt5.QtCore import QTime, Qt, QDate
hubpath = "LightPosition.csv"
########################################################################################################################
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
           # self.starttimeedit.setTime(self.presenttimehour,self.presenttimemin,self.presenttimesec)
            self.setbutton.hide()
        else:
            self.Shift.click()
            self.stoptimeedit.show()
            self.starttimeedit.show()
            self.label_StartTime.show()
            self.label_StopTime.show()
            print(ServerConfigDict["On Time"])

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
class Hub_Details(QtWidgets.QDialog):
    def __init__(self):
        super(Hub_Details, self).__init__()
        self.setWindowTitle("HUB Details")
        self.setWindowIcon(QtGui.QIcon("./Resources/About.png"))
        self.setFixedSize(600,700)

        self.Titlelist=["LightID", "LightIP","Area"]

        self.SaveFlag=True

        self.tableWidget = QTableWidget (self)
        self.tableWidget.setGeometry(QtCore.QRect(10,100,580,580))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(("LightID", "LightIP","Area"))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)
        self.tableWidget.setFont(font)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setSelectionMode(self.tableWidget.SingleSelection)

        self.lineEdit_HubID = QLineEdit(self)
        self.lineEdit_HubID.setPlaceholderText("Area")
        self.lineEdit_HubID.setFont(font)
        self.lineEdit_HubID.setGeometry(20,10,200,30)

        self.lineEdit_HubIP = QLineEdit(self)
        self.lineEdit_HubIP.setPlaceholderText("Cam IP")
        self.lineEdit_HubIP.setFont(font)
        self.lineEdit_HubIP.setGeometry(370, 10, 200, 30)
        self.lineEdit_HubIP.setAlignment(QtCore.Qt.AlignHCenter)
        self.lineEdit_HubIP.setInputMask("000.000.000.000")

        self.PB_Modify = QPushButton('Modify', self)
        self.PB_Modify.setIcon(QIcon("Resources/modify.png"))
        self.PB_Modify.setGeometry(QtCore.QRect(230, 50, 130, 31))

        self.PB_Save = QPushButton('Save', self)
        self.PB_Save.setIcon(QIcon("Resources/Save.png"))
        self.PB_Save.setGeometry(QtCore.QRect(420, 50, 130, 31))
        self.PB_Save.clicked.connect(self.SavetoDisc)

        self.PB_Modify.clicked.connect(self.Modify)
        self.tableWidget.cellClicked.connect(self.cell_was_clicked)

    def SavetoDisc(self):
        if (self.tableWidget.rowCount() != 0):
            for row in range(self.tableWidget.rowCount()):
                column = 1
                item = self.tableWidget.item(row, column)
                if item is not None:
                    if (IP_Vallidator.isIPValid(item.text()) == False):
                        QMessageBox.warning(QMessageBox(), "WARNING!!",
                                            f"Invalid IP address at Row {row + 1}\n{item.text()}")
                        self.tableWidget.selectRow(row)
            if self.SaveFlag == True:
                path = []
                path.append(hubpath)
            else:
                path = QFileDialog.getSaveFileName(self, "Save CSV", os.getenv("Home"),"CSV(*.csv)")
            for row in range(self.tableWidget.rowCount()):
                column = 1  #Camera Ip Validity
                item = self.tableWidget.item(row, column)
                if item is not None:
                    if (IP_Vallidator.isIPValid(item.text()) == True):
                        # print(item.text())
                        if path[0] != "":
                          #  Titlelist = ['Zone', 'Sensitivity','HUB ID', 'Channel', 'Sensor ID', 'Camera IP', 'Camera ID', 'Preset']
                            with open(path[0], 'w') as stream:
                                rowdata = []
                                writer = csv.writer(stream, lineterminator='\n')
                                for column in range(len(self.Titlelist)):
                                    Title = self.Titlelist[column]
                                    rowdata.append(Title)
                                writer.writerow(rowdata)
                                for row in range(self.tableWidget.rowCount()):
                                    rowdata = []
                                    for column in range(self.tableWidget.columnCount()):
                                        item = self.tableWidget.item(row, column)
                                        if item is not None:
                                            rowdata.append(item.text())
                                        else:
                                            rowdata.append('')
                                    writer.writerow(rowdata)
                    else:
                        QMessageBox.warning(QMessageBox(), "WARNING!!", item.text() + "  you entered is Invalid IP address")
                        print("Error in Row", row + 1, "Column", column)
        QMessageBox.information(QMessageBox(), "Information","Saved successfully")
        self.tableWidget.clear()
        self.close()


    def Modify(self):
        selRanges = self.tableWidget.selectedRanges()
        if (len(selRanges) > 0):
            # print('length of ranges',len(selRanges))
            # selRanges.sort()
            trashrows = []
            for i in range(len(selRanges)):
                selRange = selRanges[i]
                topRow = selRange.topRow()
                bottomRow = selRange.bottomRow()
                for row in range(topRow, bottomRow + 1):
                    trashrows.append(row + 1)
                trashrows.sort()
            reply = QMessageBox.question(self, 'Confirm Modify', f'Are you sure to Modify?\nRow list: {trashrows}',
                                         QMessageBox.Yes | QMessageBox.No)
            trashrows.sort(reverse=True)
            # print(trashrows)
            if reply == QMessageBox.Yes:
                if len(self.lineEdit_HubID.text()) == 0:
                    QMessageBox.warning(QMessageBox(), "WARNING!!", "Enter Camera ID")
                else:
                    for row in trashrows:
                        if IP_Vallidator.isIPValid(self.lineEdit_HubIP.text())==True:
                            self.tableWidget.setItem(row - 1, 2, QTableWidgetItem(self.lineEdit_HubID.text()))
                            self.tableWidget.setItem(row - 1, 1, QTableWidgetItem(self.lineEdit_HubIP.text()))
                        elif IP_Vallidator.isIPValid(self.lineEdit_HubIP.text()) == False:
                            QMessageBox.warning(self, 'Invalid', "Invalid IP Address "+str(self.lineEdit_CamIP.text()))

    def cell_was_clicked(self):

        row = self.tableWidget.currentRow()

        self.lineEdit_HubID.setText(self.tableWidget.item(row,2).text())
        self.lineEdit_HubIP.setText(self.tableWidget.item(row,1).text())
    ####################################################################################################################
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        title = "Light Controller"
        left = 500
        top = 300
        width = 800
        height = 650
        self.setFixedSize(800,650)
        iconName = "icon.png"
        self.ServerStopFlag = False
        self.ClearDispCount = 0
        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(iconName))
        self.UiComponents()
        self.show()
      #  self.Text.append("Server Started")
        self.Server_Start()
        ####################################################################################################################
    def UiComponents(self):
        self.healthflag = True
        App.aboutToQuit.connect(self.Exit)

        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QtCore.QSize(56, 35))
        self.toolbar.setStyleSheet("background-color : transparent")

        self.health = QAction(self)
        self.health.setIcon(QIcon("Resources/Health.png"))
        self.health.triggered.connect(self.healthshow)

        self.button = QAction("Start Server", self)
        self.button1 = QAction("Stop Server",self)
        self.button.setIcon(QIcon("Resources/startserver.png"))
        self.button1.setIcon(QIcon("Resources/StopServer.png"))
        self.button2 = QPushButton("Send Command",self)
        self.button2.move(50,50)
        self.button2.setGeometry(QRect(510,525,200,40))
        self.button.triggered.connect(self.Server_Start)
        self.button1.triggered.connect(self.Server_Stop)
        self.button2.clicked.connect(self.LightControl)
        self.button.setEnabled(False)
        self.button2.hide()
        self.settings = QAction(self)
        self.settings.setIcon(QIcon("Resources/Clock.jpg"))
        self.settings.triggered.connect(self.TimerSetter)
        self.lightSettings = QAction(self)
        self.lightSettings.setIcon(QIcon("Resources/Light-settings.png"))
        self.lightSettings.triggered.connect(self.Launch)
        self.toolbar.addAction(self.health)
        self.toolbar.addAction(self.button)
        self.toolbar.addAction(self.button1)
        self.toolbar.addAction(self.settings)
        self.toolbar.addAction(self.lightSettings)
        self.addToolBar(self.toolbar)
        self.CurrentLightState = 'OFF'
        self.LightContrlInfo = {
                                'IPAddr' : None,
                                'Channel' : 'Left',
                                'Status' : 'OFF'
                                }
        self.label_IP_Address = QtWidgets.QLabel(self)
        self.label_IP_Address.setText("IP Address")
        self.label_IP_Address.setGeometry(70,320,100,30)
        self.label_IP_Address.hide()

        self.label_Channel = QtWidgets.QLabel(self)
        self.label_Channel.setText("Channel")
        self.label_Channel.setGeometry(270, 320, 100, 30)
        self.label_Channel.hide()

        self.label_Status = QtWidgets.QLabel(self)
        self.label_Status.setText("Status")
        self.label_Status.setGeometry(470, 320, 100, 30)
        self.label_Status.hide()

        self.combo_IP_Address = QtWidgets.QComboBox(self)
        self.combo_IP_Address.setGeometry(30, 350, 150, 30)
        self.combo_IP_Address.hide()
        self.combo_IP_Address.addItems(["192.168.1.50","192.168.1.51","192.168.1.52","192.168.1.53","192.168.1.54","192.168.1.55","192.168.1.56","192.168.1.57","192.168.1.58","192.168.1.59","192.168.1.60"])

        self.combo_channel = QtWidgets.QComboBox(self)
        self.combo_channel.setGeometry(230, 350, 150, 30)
        self.combo_channel.addItems(["Only Left","Only Right","Both Left & Right"])
        self.combo_channel.hide()

        self.combo_status = QtWidgets.QComboBox(self)
        self.combo_status.setGeometry(430, 350, 150, 30)
        self.combo_status.addItems(["ON","OFF"])
        self.combo_status.hide()

        self.central_light = QPushButton(self)
        self.central_light.setIcon(QIcon("Resources/Light.png"))
        self.central_light.setStyleSheet("background-color:transparent;")
        self.central_light.setIconSize(QSize(500, 500))
        self.central_light.setGeometry(200, 100, 380, 440)

        self.zone_light1 = QPushButton("Zone1 Light \nCentroller 1", self)
        self.zone_light1.setStyleSheet("background-color:transparent;")
        self.zone_light1.setIconSize(QSize(400, 400))
        self.zone_light1.setGeometry(320, 40, 100, 50)

        self.zone_light2 = QPushButton("Zone1 Light \nCentroller 2", self)
        self.zone_light2.setStyleSheet("background-color:transparent;")
        self.zone_light2.setIconSize(QSize(400, 400))
        self.zone_light2.setGeometry(250, 80, 100, 50)

        self.zone_light3 = QPushButton("Zone2 Light \nCentroller 3",self)
        self.zone_light3.setStyleSheet("background-color:transparent;")
        self.zone_light3.setIconSize(QSize(400, 400))
        self.zone_light3.setGeometry(150, 110, 100, 50)

        self.zone_light4 = QPushButton("Zone2 Light \nCentroller 4", self)
        self.zone_light4.setStyleSheet("background-color:transparent;")
        self.zone_light4.setIconSize(QSize(400, 400))
        self.zone_light4.setGeometry(130, 190, 100, 50)

        self.zone_light5 = QPushButton("Zone3 Light \nCentroller 5", self)
        self.zone_light5.setStyleSheet("background-color:transparent;")
        self.zone_light5.setIconSize(QSize(400, 400))
        self.zone_light5.setGeometry(80, 260, 100, 50)

        self.zone_light6 = QPushButton("Zone4 Light \nCentroller 6", self)
        self.zone_light6.setStyleSheet("background-color:transparent;")
        self.zone_light6.setIconSize(QSize(400, 400))
        self.zone_light6.setGeometry(130, 320, 100, 50)

        self.zone_light7 = QPushButton("Zone4 Light \nCentroller 7", self)
        self.zone_light7.setStyleSheet("background-color:transparent;")
        self.zone_light7.setIconSize(QSize(400, 400))
        self.zone_light7.setGeometry(150, 410, 100, 50)

        self.zone_light8 = QPushButton("Zone4 Light \nCentroller 8", self)
        self.zone_light8.setStyleSheet("background-color:transparent;")
        self.zone_light8.setIconSize(QSize(400, 400))
        self.zone_light8.setGeometry(180, 480, 100, 50)

        self.zone_light9 = QPushButton("Zone5 Light \nCentroller 9", self)
        self.zone_light9.setStyleSheet("background-color:transparent;")
        self.zone_light9.setIconSize(QSize(400, 400))
        self.zone_light9.setGeometry(340, 550, 100, 50)

        self.zone_light10 = QPushButton("Zone5 Light \nCentroller 10", self)
        self.zone_light10.setStyleSheet("background-color:transparent;")
        self.zone_light10.setIconSize(QSize(400, 400))
        self.zone_light10.setGeometry(480, 480, 100, 50)

        self.zone_light11 = QPushButton("Zone5 Light \nCentroller 11", self)
        self.zone_light11.setStyleSheet("background-color:transparent;")
        self.zone_light11.setIconSize(QSize(400, 400))
        self.zone_light11.setGeometry(510, 410, 100, 50)

        self.zone_light12 = QPushButton("Zone6 Light \nCentroller 12", self)
        self.zone_light12.setStyleSheet("background-color:transparent;")
        self.zone_light12.setIconSize(QSize(400, 400))
        self.zone_light12.setGeometry(540, 320, 100, 50)

        self.zone_light13 = QPushButton("Zone6 Light \nCentroller 13", self)
        self.zone_light13.setStyleSheet("background-color:transparent;")
        self.zone_light13.setIconSize(QSize(400, 400))
        self.zone_light13.setGeometry(580, 260, 100, 50)

        self.zone_light14 = QPushButton("Zone7 Light \nCentroller 14", self)
        self.zone_light14.setStyleSheet("background-color:transparent;")
        self.zone_light14.setIconSize(QSize(400, 400))
        self.zone_light14.setGeometry(530, 190, 100, 50)

        self.zone_light15 = QPushButton("Zone7 Light \nCentroller 15", self)
        self.zone_light15.setStyleSheet("background-color:transparent;")
        self.zone_light15.setIconSize(QSize(400, 400))
        self.zone_light15.setGeometry(500, 110, 100, 50)

        self.zone_light16 = QPushButton("Zone7 Light \nCentroller 16", self)
        self.zone_light16.setStyleSheet("background-color:transparent;")
        self.zone_light16.setIconSize(QSize(400, 400))
        self.zone_light16.setGeometry(410, 70, 100, 50)

        self.Text = QTextEdit(self)
        self.Text.setReadOnly(True)
        self.Text.move(0, 50)
        self.Text.resize(800, 300)
        self.Text.hide()

        self.HubPositions = pd.read_csv('LightPosition.csv')
    def Launch(self):
        self.Details = Hub_Details()
        self.Details.tableWidget.setRowCount(len(self.HubPositions))
        for i in range(len(self.HubPositions)):
            self.Details.tableWidget.setItem(int(i), 0, QTableWidgetItem(str(self.HubPositions['HubID'].iloc[i])))
            self.Details.tableWidget.setItem(int(i), 1, QTableWidgetItem(str(self.HubPositions['HubIP'].iloc[i])))
            self.Details.tableWidget.setItem(int(i), 2, QTableWidgetItem(str(self.HubPositions['Area'].iloc[i])))
            self.Details.show()
    ####################################################################################################################
    def TimerSetter(self):
        self.LightTimer = Time_Set()
        self.LightTimer.show()

    def healthshow(self):
        if self.healthflag==True:
            self.healthflag=False
            self.Text.show()
        else:
            self.healthflag=True
            self.Text.hide()
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
