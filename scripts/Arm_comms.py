import sys, time
from os import system, name

from sockets_TFM import *
from comRT3_TFM import *

print("\n----------CONNECTION PARAMETERS-----------\n")
SockData.IP = "192.168.100.115"
SockData.Port = 10003

print("IP = %s / PORT = %i\n" %(SockData.IP,SockData.Port))
# input("\nIs it all right? [Enter] / [Ctrl+C] ")

print("\n")

destSocket = CreateSocket(SockData)     #Communication for vision and playing data
RT3_address, commands, RT3_sock = initRT3COM(SockData)      #Communciation for RT3 Commands

initRobot(RT3_sock, RT3_address, commands)      #Initialize Robot configuration
time.sleep(0.5)

#Load MAIN Program and start the application
loadProgram(RT3_sock, RT3_address, commands, "TEST")

print("Program Loaded")

#Run the Robot
runRobot(RT3_sock, RT3_address, commands)
robotCOM, robotIP = ConnectRobot(destSocket)

print("Waiting the robot...\n")

DataTransmission(SockData,robotCOM,SockData.Port.encode('utf-8'))
closeCOM(RT3_address, RT3_sock,commands)

sys.exit()
