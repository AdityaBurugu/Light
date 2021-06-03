########################################################################################################################
from datetime import datetime
import json
import socket,selectors,types

########################################################################################################################
from PyQt5 import QtCore

class LightController(QtCore.QThread):
    # Create a counter thread
    change_value = QtCore.pyqtSignal(str)
   # postevent = QtCore.pyqtSignal(dict)
   # posthealthevent = QtCore.pyqtSignal(dict)
    ####################################################################################################################
    def __init__(self):
        super().__init__()
        self.StopFlag = False
        self.LightCntrlFlag = False
        self.LightContrlInfo = {
                                'IPAddr' : None,
                                'Channel' : 'Left',
                                'Status' : 'OFF'
                                }
        self.ServerIP = 'localhost'
        self.Port = 5556
    ####################################################################################################################
    def run(self):
        GUI_CONNECT = b'Command Controller'
        GUI_Client_Conn_Status = False
        GUI_sock = None
        sel = selectors.DefaultSelector()
        # host = '192.168.1.150'  # Standard loopback interface address (localhost)
        # host = 'DESKTOP-E9LCLCN'  # Standard loopback interface address (localhost)
        port = self.Port  # Port to listen on (non-privileged ports are > 1023)
        # host = socket.gethostname()
        # IPAddr = socket.gethostbyname(host)
        IPAddr =self.ServerIP
        # self.change_value.emit("Your Computer Name is:" + host)
        # self.change_value.emit("Your Computer IP Address is:" + IPAddr)
        try:
            lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            lsock.settimeout(1)
            lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            lsock.bind((IPAddr, port))
            lsock.listen()
            self.change_value.emit(f'listening on :({self.ServerIP},{self.Port})')
            # print('listening on', (host, port))
            lsock.setblocking(False)
            sel.register(lsock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=None)
        except:
            self.change_value.emit(f'LAN inactive or set IP Address of Computer to {IPAddr}')
            return
        ################################################################################################################
        def accept_wrapper(sock):
            # print('trying for connection')
            conn, addr = sock.accept()  # Should be ready to read
            self.change_value.emit(f'{datetime.now().today().strftime("%d-%m-%Y %H:%M:%S")} accepted connection from {addr}')
            # print('accepted connection from', addr)
            #sock.send(b'aaaaaa')
            conn.setblocking(False)
            data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
            sel.register(conn, events, data=data)
            return conn, addr
        activesocklist = []
        activeLightCntrList = []
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        while self.StopFlag == False:
            if self.LightCntrlFlag == True:
                self.LightCntrlFlag = False
               # print('Bhaskar')
                print(activesocklist)
                print(activeLightCntrList)
                try:
                    LightCntrlindex = activeLightCntrList.index(self.LightContrlInfo['IPAddr'])
                    print('########## Index',LightCntrlindex)
                except:
                    LightCntrlindex = -1
                    print('Inactive Light Controller')
                if LightCntrlindex >=0:
                    if self.LightContrlInfo['Channel'] == 'Only Left':
                        print('sending Left Command')
                        if self.LightContrlInfo['Status'] == 'ON':
                            #sock.send(b'(|SETOUTA=A|)[EC]')
                            activesocklist[LightCntrlindex].send(b'(|SETOUTA=A|)[EC]')
                        else:
                            #sock.send(b'(|SETOUTA=I|)[F4]')
                            activesocklist[LightCntrlindex].send(b'(|SETOUTA=I|)[F4]')
                    elif self.LightContrlInfo['Channel'] == 'Only Right':
                        print('sending Right Command')
                        if self.LightContrlInfo['Status'] == 'ON':
                            #sock.send(b'(|SETOUTB=A|)[ED]')
                            activesocklist[LightCntrlindex].send(b'(|SETOUTB=A|)[ED]')
                        else:
                            #sock.send(b'(|SETOUTB=I|)[F5]')
                            activesocklist[LightCntrlindex].send(b'(|SETOUTB=I|)[F5]')
                    elif self.LightContrlInfo['Channel'] == 'Both Left & Right':
                        print('sending Both Command')
                        if self.LightContrlInfo['Status'] == 'ON':
                            #sock.send(b'(|SETOUTA=A|SETOUTB=A|)[0C]')
                            activesocklist[LightCntrlindex].send(b'(|SETOUTA=A|SETOUTB=A|)[0C]')
                        else:
                            #sock.send(b'(|SETOUTA=I|SETOUTB=I|)[1C]')
                            activesocklist[LightCntrlindex].send(b'(|SETOUTA=I|SETOUTB=I|)[1C]')
            try:
                events = sel.select(timeout=1)
            except:
                print("error")
            for key, mask in events:
                try:
                    if key.data is None:
                        # print('if condition')
                        # print(key.fileobj)
                        conn, addr1 = accept_wrapper(key.fileobj)
                        #    print(conn,addr1)
                       # key.fileobj.send(b'aaaaaa')
                        activesocklist.append(conn)
                        activeLightCntrList.append(addr1[0])
                    else:
                        sock = key.fileobj
                        data = key.data
                        # data = service_connection(key, mask)
                        if mask & selectors.EVENT_READ:
                            recv_data = sock.recv(1024)  # Should be ready to read
                            if recv_data:
                                #print(recv_data)
                                try:
                                    JsonCmdDict = json.loads(recv_data)
                                    print(JsonCmdDict)
                                    self.LightContrlInfo['IPAddr'] = JsonCmdDict['IPAddr']
                                    self.LightContrlInfo['Channel'] = JsonCmdDict['Channel']
                                    self.LightContrlInfo['Status'] = JsonCmdDict['Status']
                                    self.LightCntrlFlag = True
                                    self.change_value.emit(f'{datetime.now().today().strftime("%d-%m-%Y %H:%M:%S")} {data.addr} {JsonCmdDict}')

                                except:
                                    print('invalid JSON')
                            else:
                                self.change_value.emit(f'{datetime.now().today().strftime("%d-%m-%Y %H:%M:%S")} closing connection to {data.addr}')
                                GUI_Client_Conn_Status = False
                                # print('GUI',GUI_IPAddr,GUI_Port)
                                # print('closing connection to', data.addr)
                                # if (data.addr == GUI_IPAddr) :
                                #    self.change_value.emit('GUI_Client Closed' )
                                sel.unregister(sock)
                                sock.close()
                                activesocklist.remove(sock)
                                activeLightCntrList.remove(addr1[0])
                                print('sock' + str(sock))
                except:
                    print('If Error')
                    print(key.fileobj)
                    s1 = key.fileobj
                    sel.unregister(s1)
                    s1.close()
                    activesocklist.remove(s1)
                    activeLightCntrList.remove(addr1[0])
                    print('Socket Closed')
        print('Number of Active Sockets', len(activesocklist))
        for s1 in activesocklist:
            sel.unregister(s1)
            s1.close()
            print(s1)
        # activesocklist.remove(sock)
        sel.unregister(lsock)
        lsock.close()
    ####################################################################################################################
    ####################################################################################################################