from flask import Flask
import random,json,time
from os import getenv
from dotenv import load_dotenv
from datetime import datetime
from threading import Thread
load_dotenv()
from flask_cors import CORS
from flask_socketio import SocketIO,emit
from flask_restful import Api,Resource
from Ser_socket import socket_rec,sendNo
from db import Db



# -*- coding: utf-8 -*-
import socket
from threading import Thread
from db import Db 
import json
import datetime,time

def socket_rec():
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
            ws = socketio
            ws.emit('getMessage',json.dumps(data))
            ws.emit('getStatus', json.dumps({'status': True,}))
            print(f'傳送給客戶端{data}')

            outdata = 'echo ' + indata.decode()
            conn.send(outdata.encode())
            conn.close()
    except KeyboardInterrupt:
        print('樹莓派socket 斷開連結')
        s.close()
    except OSError:
        print('port被佔用，請確認')

def sendNo():
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
            ws = socketio
            ws.emit('getStatus', json.dumps({'status': False,}))
            sec = 0



# Flask app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = getenv("SECRET")

# socketio
global socketio
socketio = SocketIO(app=app, cors_allowed_origins="*")

# restful api
api = Api(app)
# cors
CORS(app, origins='http://localhost:3000')

# 是否有人
status = False

class walk(Resource):

    def get(self):
        from datetime import datetime
        # 取得目前時間
        current_time = datetime.now()
        # 取得目前小時
        current_hour = int(current_time.hour)
        data = Db().search_records_by_time(current_hour-1,current_hour+1)
        total = 0
        for i in data:
            total += i[4]
        print(total)
        return({'total':total})

@socketio.on("connect")
def connected():
    """event listener when client connects to the server"""
    print("-------------------")
    status = True
    print("client has connected")
    Thread(target=Test_data).start()
    Thread(target=sendNo).start()

    
@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the server"""
    print("user disconnected")

def Test_data():
    from datetime import datetime 
    import time
    zjy = [1,5,5,5,3,4,4] ; times = 0
    while True:
        
        data = {
            'date':datetime.now().strftime("%Y/%m/%d"),
            'time':datetime.now().strftime("%H:%M:%S"),
            'walk':random.randrange(1,10)
        }
        time_ob = datetime.now()
        Db().create_walk_record(record_date=time_ob.date(),record_time=time_ob.time(),num_people=int(data['walk']))
        socketio.emit('getMessage',json.dumps(data))
        socketio.emit('getStatus',json.dumps({'status':True}))
        time.sleep(zjy[times])
        times += 1 
        if times > 6:
            print('測試完畢')
            break
            

    

@socketio.on('client_event')
def client_msg(msg):
    print(msg)

@socketio.on('getStatus')
def getStatus():
    if status:
        socketio.emit('getStatus',json.dumps({'status':True}))
    else:
        socketio.emit('getStatus',json.dumps({'status':False}))

@socketio.on('getMessage')
def connected_msg(msg):
    socketio.emit('getMessage','hello World')

# setting api resource
api.add_resource(walk, '/walk')



if __name__ == '__main__':
    try:
        t_rasp = Thread(target=socket_rec)
        t_rasp.start()

        t_no = Thread(target=sendNo)
        t_no.start()
        socketio.run(app,host=f'{getenv("HOST")}',port=getenv("PORT"),allow_unsafe_werkzeug=True)
        app.run(host=f'{getenv("HOST")}',port=getenv("PORT"))
    except KeyboardInterrupt:
        print('伺服器關閉')
        import sys
        sys.exit()
    except Exception as e:
        print(f'problem occured:{e}')
