import RPi.GPIO as GPIO
from datetime import datetime
import json
import socket
import time
import os
from dotenv import load_dotenv

class Main():
    def __init__(self) -> None:
        load_dotenv()
        self.ip = os.getenv("SERVER_IP")  
        self.port = int(os.getenv("SERVER_PORT")) 

        self.sec = 0
        self.total = 0
        self.people = 0

        self.pin_light = int(os.getenv("SENSOR_light"))
        self.pin_red = int(os.getenv("SENSOR_red"))

        self.connection = None
        print(f"IP:{self.ip}"); print(f"PORT:{self.port}")
    
    def detect(self):
        try:
            GPIO.setmode(GPIO.BOARD)
            # 設定GPIO腳位為輸出
            GPIO.setup(self.pin_light, GPIO.OUT)
            # 設定GPIO腳位為輸入
            GPIO.setup(self.pin_red, GPIO.IN)
            
            while True:
                self.people += 2
                self.sec += 1
                time.sleep(1)
                
                if GPIO.input(self.pin_red):
                    print("紅外線偵測到物體！")
                    # 點亮LED燈
                    GPIO.output(self.pin_light, GPIO.HIGH)
                    self.__test()
                    
                else:
                    print("未偵測到物體")
                    # 關閉LED燈
                    GPIO.output(self.pin_light, GPIO.LOW)
                     
                                
                self.people = 0  # 正確的賦值方式

                if self.sec == 300:
                    self.sec = 0
                    # self.__message_min(walk=self.total)
                    # self.connection.close()
                    self.total = 0

        except Exception as e:
            print(f'樹莓派系統出現問題{e}')
            
        except KeyboardInterrupt:
            print("樹莓派停止運作！")
            
        finally:
            GPIO.cleanup()
            print('斷開Server連結')
            
    def __message(self,data):
        """傳遞訊息及建立socket"""
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((self.ip, self.port))
            json_data = json.dumps(data)
            self.connection.sendall(bytes(json_data, encoding='utf-8'))
            print('資料success')
        except Exception as e:
            print(f"傳遞訊息時發生錯誤: {e}")
        finally:
            self.connection.close()
            print("連線已關閉")
    
    def __test(self):
        import random
        curret_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {"name": "walk", "time": curret_time, 'walk': random.randrange(1, 5)}
        self.__message(data)
        


Main().detect()
