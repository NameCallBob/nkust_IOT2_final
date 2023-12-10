# -*- coding: utf-8 -*-
import socket
from threading import Thread
import flask_socketio
from db import Db 
import json
import datetime,time

def socket_rec(ws:flask_socketio.SocketIO):
    """
    建立與樹莓派的socket tcp
    """
    HOST = '0.0.0.0'
    PORT = 8000
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((HOST, PORT))
        s.listen(5)

        print('伺服器： %s:%s' % (HOST, PORT))
        print('準備連結')
    
        while True:
            conn, addr = s.accept()
            print('connected by ' + str(addr))
            
            indata = conn.recv(1024)
            data = indata.decode()
            rec = json.loads(data)
            date_time_obj = rec["time"].split(" ")
            t_date = date_time_obj[0]
            t_time = date_time_obj[1]
            Db().create_walk_record(
                area="木椅區",
                record_date=t_date,
                record_time=t_time,
                num_people=int(rec['walk']),
            )
            """資料再處理"""
            data = {
                'date':t_date,
                'time':t_time,
                'walk':int(rec['walk']),
            }
            
            ws.emit('getMessage', json.dumps(data))
            ws.emit('getStatus', json.dumps({'status': True}))
            print(f'傳送給客戶端{data}')

            outdata = 'echo ' + indata.decode()
            conn.send(outdata.encode())
            conn.close()
    except KeyboardInterrupt:
        print('樹莓派socket 斷開連結')
        s.close()
    except OSError:
        print('port被佔用，請確認')

def sendNo(ws:flask_socketio.SocketIO):
    """
    每過五秒偵測是否有接收到訊息
    無 則寄false
    """
    import time
    sec = 0 ;
    while True:
        time.sleep(1)
        sec += 1 
        if sec > 5:
            print('Sending status: False')
            ws.emit('getStatus', json.dumps({'status': False,}))
            sec = 0

