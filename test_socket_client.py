import socket,time,json
from datetime import datetime


s =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    time.sleep(1)
    s.connect(('127.0.0.1',8000))
    import random
    curret_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {"name": "walk", "time": curret_time, 'walk': random.randrange(1, 50)}

    s.sendall(bytes(json.dumps(data),encoding='utf-8'))
    s.close()