import serial
import sys
import tty
import termios
import threading
import socket

ser = serial.Serial("/dev/ttyACM0", 9600)

flag = 0

def getkey():
    fd = sys.stdin.fileno()
    original_attributes = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, original_attributes)
    return ch

def control():
    global flag
    b = 100
    OCR3A = 1950
    OCR3B = 1950

    while True:
        command = getkey()
        ser.write(command.encode())
        
        if command == '+':
            b = b + 5
            if b>= 100:
                b = 100
            print("PWM :",b)
        
        elif command == '-':
            b = b - 5
            if b<= 0:
                b = 0
            print("PWM :",b)

        elif command == 'p':
            flag = 1
            print("auto off")
        elif command == 'o':
            flag = 0
            print("auto on")

        elif command == '\x1b':
            break

def threaded(client_socket, addr):
    global flag
    message = 'a'
    k = 'k'
    j = 'j' 
    print('Connected by :', addr[0], ':', addr[1]) 
    while True: 
        try:
            data = client_socket.recv(1024)
            if data.decode() == 'f':
                if flag == 0:
                    ser.write(k.encode())
                else if flag == 1:
                    ser.write(j.encode())
            if data.decode() == 'a':
                pass
        except ConnectionResetError as e:
            print('Disconnected by ' + addr[0],':',addr[1])
            break
    client_socket.close() 


t1 = threading.Thread(target=control)
t1.daemon = True
t1.start()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('192.168.0.101', 9999)) 
server_socket.listen() 

while True:
    client_socket, addr = server_socket.accept()
    t2 = threading.Thread(target=threaded,args=(client_socket,addr))
    t2.daemon = True
    t2.start()
g.cleanup()
server_socket.close() 

