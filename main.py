import threading
import time
import math

eventNewPacketContiki = threading.Event()
eventNewPacketSecuPAN = threading.Event()

lockAttackContiki = threading.Lock()
lockAttackSecuPAN = threading.Lock()

threads = []
exitFlag = 0

totalPacketSent = 0
totalPacketReceivedContiki = 0
totalPacketReceivedSecuPAN = 0;

totalTimeContiki = 0
totalTimeSecuPAN = 0

attackFlagContiki = 0
attackFlagSecuPAN = 0

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


def controller():
    global exitFlag
    print('controller Thread: controller thread started')
    time.sleep(simulationTime);
    print('controller Thread: simulation time is over')
    exitFlag = 1;
    eventNewPacketContiki.set()
    eventNewPacketSecuPAN.set()
    print('Controller Thread: controller thread ended')


def sender():
    print('Sender thread: sender thread started')
    global exitFlag
    global totalPacketSent
    while exitFlag == 0:
        totalPacketSent = totalPacketSent + 1
        print('Sender thread: sending a packet')
        eventNewPacketSecuPAN.set()
        eventNewPacketContiki.set()
        time.sleep(packetSendingInterval)
    print('Sender thread: sender thread ended')


def receiverContiki():
    print("Receiver Thread (Contiki): reciever started")
    global exitFlag
    global totalPacketReceivedContiki
    global attackFlagContiki
    global totalTimeContiki

    while exitFlag == 0:
        print("Receiver Thread (Contiki): waiting for packet to arrive")
        eventNewPacketContiki.clear()  # need to take care the position of the .clear method
        eventNewPacketContiki.wait()
        print("Receiver Thread (Contiki): packet received")
        totalPacketReceivedContiki = totalPacketReceivedContiki + 1
        totalTimeContiki = totalTimeContiki + endToEndDelayForAllFragment

        lockAttackContiki.acquire()
        if attackFlagContiki:
            attackFlagContiki = 0
            lockAttackContiki.release()
            print("Receiver Thread (Contiki): attack occured")
            totalTimeContiki = totalTimeContiki + endToEndDelayForAllFragment
            print("Receiver Thread (Contiki): Going to sleep due to attack (Contiki)")
            time.sleep(endToEndDelayForAllFragment / 1000)

        else:
            lockAttackContiki.release()

def receiverSecuPAN():
    print("Receiver Thread (SecuPAN): receiver started")
    global exitFlag
    global totalPacketReceivedSecuPAN
    global attackFlagSecuPAN
    global totalTimeSecuPAN

    while exitFlag == 0:
        print("Receiver Thread (SecuPAN): waiting for packet to arrive")
        eventNewPacketSecuPAN.clear()  # need to take care the position of the .clear method
        eventNewPacketSecuPAN.wait()
        print("Receiver Thread (SecuPAN): packet received")
        totalPacketReceivedSecuPAN = totalPacketReceivedSecuPAN + 1
        totalTimeSecuPAN = totalTimeSecuPAN + endToEndDelayForAllFragment

        lockAttackSecuPAN.acquire()
        if attackFlagSecuPAN:
            attackFlagSecuPAN = 0
            lockAttackSecuPAN.release()
            print("Receiver Thread (SecuPAN): attack occured")
            print("Receiver Thread (SecuPAN): Going to sleep due to attack (SecuPAN)")
            time.sleep(endToEndDelayForSingleFragment / 1000)
            totalTimeSecuPAN = totalTimeSecuPAN + endToEndDelayForSingleFragment
        else:
            lockAttackSecuPAN.release()

def attacker():
    print("Attacker Thread: Attacker thread started")
    global exitFlag
    global attackFlagContiki
    global attackFlagSecuPAN

    while exitFlag == 0:
        time.sleep(attackInterval)

        lockAttackContiki.acquire()
        print("Attacker Thread: preforming attack on Contiki")
        attackFlagContiki = 1
        lockAttackContiki.release()

        lockAttackSecuPAN.acquire()
        print("Attacker Thread: preforming attack on SecuPAN")
        attackFlagSecuPAN = 1
        lockAttackSecuPAN.release()

    print("Attacker Thread: Attacker thread ended")


t = threading.Thread(target=sender)
threads.append(t)
t.start()

t = threading.Thread(target=receiverContiki)
threads.append(t)
t.start()

t = threading.Thread(target=receiverSecuPAN)
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


print("Total Number of Packets Sent %d" %(totalPacketSent))

print("Total Number of Packet Received (Contiki) %d" %(totalPacketReceivedContiki))
print ("Total time taken for receving pacekts (Contiki): %d ms" %(totalTimeContiki))


print("Total Number of Packet Received (SecuPAN) %d" %(totalPacketReceivedSecuPAN))
print ("Total time taken for receving pacekts (SecuPAN): %d ms" %(totalTimeSecuPAN))