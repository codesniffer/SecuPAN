import socket, sys, time, threading

packet_sent = 0
packet_delivered = 0
HOST, PORT = "localhost", 9999
client_naive = "naive"
data_naive = "data naive"

client_attacker = "attacker"
data_attacker = "data attacker"

pdrThreadSleepTime = 5 # print PDR every 5 sec

#this configuration is for base-contiki client. Uncomment this config and comment the config below when you want to generate PDR for base-contiki
#packetSendingIntervalNaive = .6 # 1 packet every 600 ms

#this configuraiton is for SecuPAN. Uncomment this config and comment the config above when you want to generate PDR for SecuPAN
packetSendingIntervalNaive = .4 # 1 packet every 600 ms

packetSendingIntervalAttacker = .2 # 1 packet every 200 ms

simulationTime = 60 * 10 # x min

exitFlag = 0

def controller():
    global exitFlag
    print('Controller Thread: controller thread started')
    time.sleep(simulationTime)
    exitFlag = 1
    print('Controller Thread: controller thread ended')
#-----------------------------------------------------------------------------#

def printPDR():
    print('PrintPDR Thread: PrintPDR thread started')
    global  packet_sent
    global  packet_delivered

    elaspedTime = 0;
    global  exitFlag

    while exitFlag == 0:
        time.sleep(pdrThreadSleepTime)
        elaspedTime = elaspedTime + pdrThreadSleepTime
        if (packet_sent > 0) :
            #print("elasped time %d, pdr %.2f" %(elaspedTime, packet_delivered/packet_sent))
            print("%d, %.2f" %(elaspedTime, packet_delivered/packet_sent)) # %d sec .2f pdr

            pass

    print('PrintPDR Thread: PrintPDR thread ended')
#-----------------------------------------------------------------------------#

def senderNaive():
    global  packet_sent
    global  packet_delivered
    global exitFlag
    print('SenderNaive Thread: SenderNaive thread started')

    while exitFlag == 0:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # connect to server
            sock.connect((HOST, PORT))
            # send data
            sock.sendall(bytes(client_naive + "," + data_naive + "\n", "utf-8"))
            # receive data back from the server
            received = str(sock.recv(1024), "utf-8")
        finally:
            # shut down
            sock.close()
        packet_sent += 1
        if received == "recieved":
            packet_delivered += 1
        else:
            #print ("SenderNaive: denied")
            pass

        #print("SenderNaive: packet sent %d, packet delivered %d" % (packet_sent, packet_delivered))
        time.sleep(packetSendingIntervalNaive)
    print('SenderNaive Thread: SenderNaive thread ended')
#-----------------------------------------------------------------------------#

def senderAttacker():
    global  packet_sent
    global  packet_delivered
    print('SendeAttacker Thread: SenderNaive thread started')

    while exitFlag == 0:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # connect to server
            sock.connect((HOST, PORT))
            # send data
            sock.sendall(bytes(client_attacker + "," + data_attacker + "\n", "utf-8"))
            # receive data back from the server
            received = str(sock.recv(1024), "utf-8")
        finally:
            # shut down
            sock.close()
        time.sleep(packetSendingIntervalAttacker)
    print('SendeAttacker Thread: SenderNaive thread ended')
#-----------------------------------------------------------------------------#

threads = []

t = threading.Thread(target=controller)
threads.append(t)
t.start()

t = threading.Thread(target=senderNaive)
threads.append(t)
t.start()

t = threading.Thread(target=senderAttacker)
threads.append(t)
t.start()

t = threading.Thread(target=printPDR)
threads.append(t)
t.start()

for t in threads:
    t.join()

print("Simulation Completed")
