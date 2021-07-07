import re
import os
import serial
import time
import socket

def readline():  
  while os.path.exists("/dev/ttyUSB0")==True:
    port = '/dev/ttyUSB0'
    ard = serial.Serial(port,115200,timeout=3,
           parity=serial.PARITY_NONE,
           bytesize=serial.EIGHTBITS,
           stopbits=serial.STOPBITS_ONE)
    try:
       incoming = ard.readline().decode('ascii')
       print(incoming)
       ard.flush()
       if  "Received" in incoming :
         HOST = socket.gethostbyname('control_socketserver')
         PORT = 8000
         client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         client.connect((HOST, PORT))
         s=re.findall("\d+",incoming)[0]
         client.send(s.encode('utf-8'))
         client.close()
         """
         s=re.findall("\d+",incoming)[0]
         print(s)
         oscmd_1="sh -c 'echo "
         oscmd_2="> /sys/devices/pwm-fan/target_pwm'"
         os.system(oscmd_1+str(s)+oscmd_2)
         """
    except:
       pass

if __name__ == '__main__' :
   while True:
     readline()
