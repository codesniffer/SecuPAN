import threading
import time
import math


event_signal_new_packet = threading.Event()

condition = threading.Condition()

lockAttack = threading.Lock()

threads = []
exitFlag = 0

totalPacketSent = 0
totalPacketReceived = 0
totalTime = 0
attackFlag = 0

simulationTime = 120 # 120 ms
packetSendingInterval = 0.3 # 300 ms

attackInterval = .5 # 500 ms second

packetSize = 128
fragmentSize = 29 # 29 bytes for mesh under-routing
numberOfFragment = math.ceil(packetSize / fragmentSize)

hopToHopDelay = 58 # 58 ms for mesh-under
numberofHops = 2
endToEndDelayForAllFragment = hopToHopDelay * numberofHops * numberOfFragment
endToEndDelayForSingleFragment = hopToHopDelay * numberofHops

contiki = 0 # without SecuPAN

#print ("sleep time for a packet %f" % (endToEndDelayForAllFragment / 1000))
#print ("sleep time for single fragment %f" % (endToEndDelayForSingleFragment / 1000))

# print('Thread got event: %s' % tname)

def controller():
    global exitFlag
    print('controller Thread: controller thread started')
    time.sleep(simulationTime);
    print('controller Thread: simulation time is over')
    exitFlag = 1;
    event_signal_new_packet.set()
    print('Controller Thread: controller thread ended')


def sender():
    print('Sender thread: sender thread started')
    global exitFlag
    global totalPacketSent
    while exitFlag == 0:
        totalPacketSent = totalPacketSent + 1
        print('Sender thread: sending a packet')
        event_signal_new_packet.set()
        time.sleep(packetSendingInterval)
    print('Sender thread: sender thread ended')


def receiver():
    print("Receiver thread started")
    global exitFlag
    global totalPacketReceived
    global attackFlag
    global totalTime

    while exitFlag == 0:
        print("Receiver Thread: waiting for packet to arrive")
        event_signal_new_packet.clear()  # need to take care the position of the .clear method
        event_signal_new_packet.wait()
        print("Receiver Thread: packet received")
        totalPacketReceived = totalPacketReceived + 1
        totalTime = totalTime + endToEndDelayForAllFragment

        lockAttack.acquire()
        if attackFlag:
            attackFlag = 0
            lockAttack.release()
            print("Receiver Thread: attack occured")
            if contiki:
                totalTime = totalTime + endToEndDelayForAllFragment
                print("Receiver Thread: Going to sleep due to attack (Contiki)")
                time.sleep(endToEndDelayForAllFragment / 1000)
            else:  # SecuPAN
                # or I can skip this delay for SecuPAN for better preformance
                print("Receiver Thread: Going to sleep due to attack (SecuPAN)")
                time.sleep(endToEndDelayForSingleFragment / 1000)
                totalTime = totalTime + endToEndDelayForSingleFragment
        else:
            lockAttack.release()


def attacker():
    print("Attacker Thread: Attacker thread started")
    global exitFlag
    global attackFlag

    while exitFlag == 0:
        time.sleep(attackInterval)
        lockAttack.acquire()
        print("Attacker Thread: preforming attack")
        attackFlag = 1
        lockAttack.release()
    print("Attacker Thread: Attacker thread ended")


t = threading.Thread(target=sender)
threads.append(t)
t.start()

t = threading.Thread(target=receiver)
threads.append(t)
t.start()

t = threading.Thread(target=attacker)
threads.append(t)
t.start()

t = threading.Thread(target=controller)
threads.append(t)
t.start()

for t in threads:
    t.join()

if contiki :
    print("Contiki Simulation Outcome")
else :
    print ("SecuPAN Simulation Outcome")

print("Total Number of Packets Sent %d" %(totalPacketSent))
print("Total Number of Packet Received %d" %(totalPacketReceived))
print ("Total time taken for receving pacekts: %d ms" %(totalTime))
