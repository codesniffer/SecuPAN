import threading
import time
import math

eventNewPacketContiki = threading.Event()
eventNewPacketSecuPAN = threading.Event()

lockAttackContiki = threading.Lock()
lockAttackSecuPAN = threading.Lock()

lockPrintResult = threading.Lock()

threads = []
exitFlag = 0

attackFlagContiki = 0
attackFlagSecuPAN = 0

simulationTime = 15 # 120 sec
packetSendingInterval = 0.3 # 300 ms

attackInterval = .5 # 500 ms second


totalPacketSent = 0



def printSimulationOutcome (scheme, routing, totalNumberOfPacketSent, totalNumberOfPacketReceived, totalTimeTakenReceivingPackets, numberOfPacketRetransmitted, totalEnergyConsumption):
    lockPrintResult.acquire()

    print ("Scheme \t\t Routing \t\t Total Number of packet Sent \t\t Total Number of Packet Received \t\t Total Time For Receiving Packets \t\t Number of Retransmitted packet \t\t Energy Consumption")
    print ("%s \t\t %s \t\t %d \t\t %d \t\t %d \t\t %d \t\t %d " %(scheme, routing, totalNumberOfPacketSent, totalNumberOfPacketReceived, totalTimeTakenReceivingPackets, numberOfPacketRetransmitted, totalEnergyConsumption))

    lockPrintResult.release()

def controller(simulation_time):
    global exitFlag
    print('controller Thread: controller thread started')
    time.sleep(simulation_time)
    print('controller Thread: simulation time is over')
    exitFlag = 1
    eventNewPacketContiki.set()
    eventNewPacketSecuPAN.set()
    print('Controller Thread: controller thread ended')

def sender(packet_sending_interval):
    print('Sender thread: sender thread started')
    global exitFlag
    global totalPacketSent
    while exitFlag == 0:
        totalPacketSent = totalPacketSent + 1
        print('Sender thread: sending a packet')
        eventNewPacketSecuPAN.set()
        eventNewPacketContiki.set()
        time.sleep(packet_sending_interval)
    print('Sender thread: sender thread ended')

def receiverContikiEx(hopToHopDelay, totalNumerOfHop, fragmentSendingEnergy, packetSize, fragmentSize, totalNumberOfFragment):
    print("Receiver Thread (Contiki): reciever started")

    global exitFlag
    global attackFlagContiki

    totalTimeForRecivingPackets = 0
    totalEnergyConsumptionForReceivingPackets = 0
    totalNumberOfReceivedPackets = 0
    totalNumberOfAttacks = 0

    endtoEndDelay = hopToHopDelay * totalNumerOfHop * totalNumberOfFragment
    energyConsumptionForSendingPacket = fragmentSendingEnergy * totalNumberOfFragment

    while exitFlag == 0:
        print("Receiver Thread (Contiki): waiting for packet to arrive")
        eventNewPacketContiki.clear()  # need to take care the position of the .clear method
        eventNewPacketContiki.wait()
        print("Receiver Thread (Contiki): packet received")
        totalTimeForRecivingPackets += endtoEndDelay
        totalEnergyConsumptionForReceivingPackets += energyConsumptionForSendingPacket
        totalNumberOfReceivedPackets += 1

        lockAttackContiki.acquire()
        if attackFlagContiki:
            attackFlagContiki = 0
            lockAttackContiki.release()
            print("Receiver Thread (Contiki): attack occured")

            totalTimeForRecivingPackets += endtoEndDelay # delay for sending the entire parcekt (all the fragments of a packet)
            totalEnergyConsumptionForReceivingPackets += energyConsumptionForSendingPacket # energy consumption for sending all the fragments of the altered packet
            totalNumberOfAttacks += 1

            print("Receiver Thread (Contiki): Going to sleep due to attack (Contiki)")
            time.sleep(endtoEndDelay / 1000)
        else:
            lockAttackContiki.release()

    printSimulationOutcome ("Contiki", "Mesh-under", totalPacketSent, totalNumberOfReceivedPackets, totalTimeForRecivingPackets,totalNumberOfAttacks,totalEnergyConsumptionForReceivingPackets)

def receiverSecuPANEx(hopToHopDelay, totalNumerOfHop, fragmentSendingEnergy, packetSize, fragmentSize, totalNumberOfFragment):
    print("Receiver Thread (SecuPAN): reciever started")

    global exitFlag
    global attackFlagSecuPAN

    totalTimeForRecivingPackets = 0
    totalEnergyConsumptionForReceivingPackets = 0
    totalNumberOfReceivedPackets = 0
    totalNumberOfAttacks = 0

    endtoEndDelay = hopToHopDelay * totalNumerOfHop * 1
    energyConsumptionForSendingPacket = fragmentSendingEnergy * totalNumberOfFragment

    while exitFlag == 0:
        print("Receiver Thread (SecuPAN): waiting for packet to arrive")
        eventNewPacketContiki.clear()  # need to take care the position of the .clear method
        eventNewPacketContiki.wait()
        print("Receiver Thread (SecuPAN): packet received")
        totalTimeForRecivingPackets += endtoEndDelay
        totalEnergyConsumptionForReceivingPackets += energyConsumptionForSendingPacket
        totalNumberOfReceivedPackets += 1

        lockAttackSecuPAN.acquire()
        if attackFlagSecuPAN:
            attackFlagSecuPAN = 0
            lockAttackSecuPAN.release()
            print("Receiver Thread (SecuPAN): attack occured")

            totalTimeForRecivingPackets += hopToHopDelay # delay for sending the fabricated/altered fragment
            totalEnergyConsumptionForReceivingPackets += fragmentSendingEnergy # energy consumption for sending the altered fragment
            totalNumberOfAttacks += 1

            print("Receiver Thread (SecuPAN): Going to sleep due to attack (SecuPAN)")
            time.sleep(endtoEndDelay / 1000)
        else:
            lockAttackSecuPAN.release()

    printSimulationOutcome ("SecuPAN", "Mesh-under", totalPacketSent, totalNumberOfReceivedPackets, totalTimeForRecivingPackets,totalNumberOfAttacks,totalEnergyConsumptionForReceivingPackets)


def attacker(attack_interval):
    print("Attacker Thread: Attacker thread started")
    global exitFlag
    global attackFlagContiki
    global attackFlagSecuPAN

    while exitFlag == 0:
        time.sleep(attack_interval)

        lockAttackContiki.acquire()
        print("Attacker Thread: preforming attack on Contiki")
        attackFlagContiki = 1
        lockAttackContiki.release()

        lockAttackSecuPAN.acquire()
        print("Attacker Thread: preforming attack on SecuPAN")
        attackFlagSecuPAN = 1
        lockAttackSecuPAN.release()

    print("Attacker Thread: Attacker thread ended")


hopToHopDelay = 58   # ms for mesh-under
totalNumerOfHop = 2  # total number of intermediate nodes including the receiving node

fragmentSendingEnergy = 10 # mj for mesh-under
packetSize = 128 # in bytes

fragmentSize = 29 # in bytes for mesh-under
totalNumberOfFragment = math.ceil(packetSize/fragmentSize)

t = threading.Thread(target=sender, args=(packetSendingInterval,))
threads.append(t)
t.start()

t = threading.Thread(target=receiverContikiEx, args=(hopToHopDelay,totalNumerOfHop,fragmentSendingEnergy,packetSize,fragmentSendingEnergy,totalNumberOfFragment,))
threads.append(t)
t.start()

t = threading.Thread(target=receiverSecuPANEx, args=(hopToHopDelay,totalNumerOfHop,fragmentSendingEnergy,packetSize,fragmentSendingEnergy,totalNumberOfFragment,))
threads.append(t)
t.start()


t = threading.Thread(target=attacker, args=(attackInterval,))
threads.append(t)
t.start()

t = threading.Thread(target=controller, args= (simulationTime,))
threads.append(t)
t.start()

for t in threads:
    t.join()

print ("All Done !!!")

#print("Total Number of Packets Sent %d" %(totalPacketSent))

#print("Total Number of Packet Received (Contiki) %d" %(totalPacketReceivedContiki))
#print ("Total time taken for receving pacekts (Contiki): %d ms" %(totalTimeContiki))


#print("Total Number of Packet Received (SecuPAN) %d" %(totalPacketReceivedSecuPAN))
#print ("Total time taken for receving pacekts (SecuPAN): %d ms" %(totalTimeSecuPAN))