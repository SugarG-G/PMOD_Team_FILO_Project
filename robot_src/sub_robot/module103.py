import threading
import RPi.GPIO as g
import sys
import tty
import termios
import time
import socket

#####################  Settings   ###########################
#ultrasonic_f
trig_f = 27
echo_f = 17

#ultrasonic_l
trig_l = 3
echo_l = 2

#ultrasonic_r
trig_r = 9
echo_r = 10

# pwm pim
pwm_pin = 18

# module motor pin(BCM)
FL1 = 23     # Front Left Forward 
FL2 = 24    # Front Left backward 
BL1 = 15    # Back Left Forward  
BL2 = 14    # Bacck Left backward
FR1 = 12    # Front Right Forward
FR2 = 16    # Front Right backward
BR1 = 20    # Back Right Forward
BR2 = 21    # Back Right Backward
# LED PIN
led = 26
# buzzer
buzz = 5
################### global variable ###########################
speed = 100
state = 0
flag = 0
ledflag = 0


command = 0
####################### Set up ##############################
g.setmode(g.BCM)
for i in [pwm_pin,trig_f,trig_l,trig_r, led, buzz, FL1, FL2, BL1, BL2, FR1, FR2, BR1, BR2]:
    g.setup(i,g.OUT)
g.setup(echo_f, g.IN)
g.setup(echo_l, g.IN)
g.setup(echo_r, g.IN)

g.output(led,1)

##################### motor pwm ###############################

pwm_all = g.PWM(pwm_pin,50)
pwm_all.start(speed)
############################# led pwm #############################
buzz_pwm = g.PWM(buzz,1)
buzz_pwm.start(0)

############################################################################################
def getkey():
    fd = sys.stdin.fileno()
    original_attributes = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, original_attributes)
    return ch

################################# direction control ########################################
def forward():

    for i in [FL1,BL1,FR1,BR1]:
        g.output(i,1)
    for i in [FL2,BL2,FR2,BR2]:
        g.output(i,0)
############################################################################################
def backward():

    for i in [FL1,BL1,FR1,BR1]:
        g.output(i,0)
    for i in [FL2,BL2,FR2,BR2]:
        g.output(i,1)
############################################################################################
def left():

    for i in [FL1,BL2,FR2,BR1]:
        g.output(i,1)
    for i in [FL2,BL1,FR1,BR2]:
        g.output(i,0)
############################################################################################
def right():

    for i in [FL2,BL1,FR1,BR2]:
        g.output(i,1)
    for i in [FL1,BL2,FR2,BR1]:
        g.output(i,0)
############################################################################################
def stop():
    for i in [FL1, FL2, BL1, BL2, FR1, FR2, BR1, BR2]:
        g.output(i,0)
############################################################################################
def right_turn():

    for i in [FL1,BL1,FR2,BR2]:
        g.output(i,1)
    for i in [FL2,BL2,FR1,BR1]:
        g.output(i,0)
############################################################################################
def left_turn():

    for i in [FL1,BL1,FR2,BR2]:
        g.output(i,0)
    for i in [FL2,BL2,FR1,BR1]:
        g.output(i,1)
#############################################################################################
def ultrasonic(trig,echo):
    
    
    g.output(trig, True)
    time.sleep(0.00001)
    g.output(trig, False)

    while g.input(echo) == 0:
        pulse_start = time.time()
    while g.input(echo) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17000
    distance = round(distance, 2)
    
    return distance

############################################################################################
def threaded(client_socket, addr):
    message = 'a' 
    print('Connected by :', addr[0], ':', addr[1]) 
    while True: 
        try:
            data = client_socket.recv(1024)
            if data.decode() == 'b':
                #stop()
                buzz_pwm.ChangeDutyCycle(90)
    
            client_socket.send(message.encode())

        except ConnectionResetError as e:
            print('Disconnected by ' + addr[0],':',addr[1])
            break
    client_socket.close() 

############################################################################################
def control():
    global command, speed, ledflag, flag, state, trig_f, trig_l, trig_r, echo_f, echo_l, echo_r
    while True:
        command = getkey()
        if command == 'w':
            forward()

        elif command == 's':
            backward()

        elif command == 'd':
            right()

        elif command == 'a':
            left()

        elif command == 'c':
            stop()
            speed = 100

        elif command == '+':
            speed += 10
            if speed >= 100:
                speed = 100
            pwm_all.ChangeDutyCycle(speed)
            print('PWM :',speed)

        elif command == '-':
            speed -= 10
            if speed <= 0:
                speed = 0
            pwm_all.ChangeDutyCycle(speed)
            print('PWM :',speed)

        elif command == 'q':
            speed = 20
            pwm_all.ChangeDutyCycle(speed)
            left_turn()

        elif command == 'e':
            speed = 20
            pwm_all.ChangeDutyCycle(speed)
            right_turn()

        elif command == 'l':
            if ledflag == 0:
                g.output(led,0)
                ledflag = 1
            elif ledflag == 1:
                g.output(led,1)
                ledflag = 0

        elif command == 'y':
            buzz_pwm.ChangeDutyCycle(0)

        elif command == 'i':
            a = ultrasonic(trig_f,echo_f)
            b = ultrasonic(trig_l,echo_l)
            c = ultrasonic(trig_r,echo_r)

            print("forward :",a,"left :",b,"right :",c)
            
        elif command == 'f':
            flag = 1
            state = 0
        
        elif command == 'g':
            flag = 2
            state = 0

        elif command == 'o':
            flag = 0
            state = 0
        elif command == '\x1b':
            flag = 0
            break
    g.cleanup()
##############################################################################################
def stop_enter():
    global speed, flag, state, trig_f, trig_l, trig_r, echo_f, echo_l, echo_r
    a = 0
    result = 0
    move_timer = 0.2
    stop_timer = 0.5
    while True:
        while flag:

            if state == 0:
                pwm_all.ChangeDutyCycle(100)
                print("state0")
                forward()
                time.sleep(move_timer)
                stop()
                time.sleep(stop_timer)
                if flag == 1:
                    result = ultrasonic(trig_l,echo_l)
                    print(result)
                    
                elif flag == 2:
                    result = ultrasonic(trig_r,echo_r)
                    print(result)
                    
                if result > 80:
                    result = 0
                    state = 1
                else: 
                    result = 0
                    state = 0
                    

            if state == 1:
                print("state1")

                backward()
                time.sleep(move_timer)
                stop()
                time.sleep(stop_timer)
                if flag == 1:
                    result = ultrasonic(trig_l,echo_l)
                    print(result)
                    
                elif flag == 2:
                    result = ultrasonic(trig_r,echo_r)
                    print(result)
                    
                
                if result <= 80:
                    a += 1
                    result = 0
                    state = 1
                else:
                    result = 0
                    state = 2

            if state == 2:
                print("state2")
                print(a)                
                for i in range(int(a/2)+1):
                    forward()
                    time.sleep(move_timer)
                    stop()
                    time.sleep(stop_timer)
                state = 3
                
    
            if state == 3:
                if flag == 1:
                    left_turn()
                elif flag == 2:
                    right_turn()
                time.sleep(0.6)
                stop()
                time.sleep(0.7)
                forward()
                pwm_all.ChangeDutyCycle(100)
                result = 0
                state = 4
            
            if state == 4:
                result = ultrasonic(trig_f,echo_f)
                if result < 10:
                    state = 5
                else:
                    state = 4
            
            if state == 5:
                time.sleep(3)
                stop()
                flag = 0
                result = 0
                a = 0
                state = 0
                
                
                print("end mode")


################################################################################################

t4 = threading.Thread(target=stop_enter)
t3 = threading.Thread(target=control)

t4.daemon = True
t3.daemon = True

t4.start()
t3.start()
############################################################################################
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('192.168.0.103', 9999)) 
server_socket.listen() 

print('server start')

while True: 
    client_socket, addr = server_socket.accept()
    t2 = threading.Thread(target=threaded,args=(client_socket,addr))
    t2.daemon = True
    t2.start()
g.cleanup()
server_socket.close() 

############################################################################################
