# echo_server.py

import socketserver, time, threading

clientInfo = dict()
clientbufferInfo = dict()
bufferSize = 1024
reAssemblyBuffer = bufferSize
messageSizeAttacker = 64  # bytes
messageSizeSender = 32 # bytes

lockBuffer = threading.Lock()
bufferResetInterval = 60 # seconds
eventBufferReset = threading.Event()

packet_sent = 0
packet_delivered = 0
pdrThreadSleepTime = 5*1 # print PDR every 5 sec


def timeKeeper():
    global  reAssemblyBuffer
    global lockBuffer

    print('TimeKeeper Thread: TimeKeeper thread started')

    while True:
        eventBufferReset.clear()  # need to take care the position of the .clear method
        eventBufferReset.wait()
        time.sleep(bufferResetInterval)
        lockBuffer.acquire()
        reAssemblyBuffer = bufferSize
        lockBuffer.release()
        print('TimeKeeper Thread: Resetting Buffer to %d' %(reAssemblyBuffer))

def printPDR():
    print('PrintPDR Thread: PrintPDR thread started')
    global  packet_sent
    global  packet_delivered

    elaspedTime = 0;

    while True :
        time.sleep(pdrThreadSleepTime)
        elaspedTime = elaspedTime + pdrThreadSleepTime
        if (packet_sent > 0) :
            #print("elasped time %d, pdr %.2f" %(elaspedTime, packet_delivered/packet_sent))
            print("%d, %.2f" %(elaspedTime, packet_delivered/packet_sent)) # %d sec .2f pdr

    print('PrintPDR Thread: PrintPDR thread ended')
#-----------------------------------------------------------------------------#

class MyTCPSocketHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        global reAssemblyBuffer
        global lockBuffer
        global packet_sent
        global packet_delivered
        self.data = self.request.recv(1024).strip()
        #print(self.data)
        client_info = self.data.decode("utf-8").split(',')

        if client_info[0] == 'attacker':
            if (reAssemblyBuffer == 0) :
                self.request.sendall(bytes("dropped", "utf-8"))
                eventBufferReset.set()
            else:
                lockBuffer.acquire()
                reAssemblyBuffer = max(reAssemblyBuffer - messageSizeAttacker, 0)
                lockBuffer.release()
                self.request.sendall(bytes("dropped", "utf-8"))
        else: # naive device
            packet_sent = packet_sent + 1
            if (reAssemblyBuffer == 0) :
                self.request.sendall(bytes("dropped", "utf-8"))
                eventBufferReset.set()
            else:
                packet_delivered = packet_delivered +1
                lockBuffer.acquire()
                reAssemblyBuffer = min (reAssemblyBuffer + messageSizeSender, bufferSize)
                lockBuffer.release()
                self.request.sendall(bytes("recieved", "utf-8"))
       # print("Buffer Remaining %d" %(reAssemblyBuffer))

if __name__ == "__main__":
    reAssemblyBuffer = 1024
    HOST, PORT = "localhost", 9999

    t = threading.Thread(target=timeKeeper)
    t.start()

    t = threading.Thread(target=printPDR)
    t.start()

    # instantiate the server, and bind to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPSocketHandler)

    # activate the server
    # this will keep running until Ctrl-C
    server.serve_forever()