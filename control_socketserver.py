import socket
import os

HOST = ''
PORT = 8000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

while True:
    conn, addr = server.accept()
    clientMessage = str(conn.recv(1024).decode('utf-8'))

    print('Client message is:', clientMessage)
    
    oscmd_1="sh -c 'echo "
    oscmd_2="> /sys/devices/pwm-fan/target_pwm'"
    os.system(oscmd_1+str(clientMessage)+oscmd_2)

    conn.close()
