import threading
import time
import math

eventNewPacketContiki = threading.Event()
eventNewPacketSecuPAN = threading.Event()

lockAttackContiki = threading.Lock()
lockAttackSecuPAN = threading.Lock()

lockPrintResult = threading.Lock()

exitFlag = 0
attackFlagContiki = 0
attackFlagSecuPAN = 0

simulationTime = 120 # 120 sec
packetSendingInterval = 0.3 # 300 ms

attackInterval = .5 # 500, 1000, and 1500 ms


totalPacketSent = 0

def printEnergyResult (simulation_time, attack_interval, scheme, routing,  number_packet_retransmitted, retransmission_energy_per_packet, total_energy_consumption):
    lockPrintResult.acquire()
    print("Simualtion Time (sec), Attack Interval (ms), Scheme, Routing, Number of Packet Retransmitted, Retransmission Energy Per Packet, Total Energy Consumption (mj)")
    print ("%d, %.2f, %s, %s, %d, %d, %d" %(simulation_time, attack_interval, scheme, routing,  number_packet_retransmitted, retransmission_energy_per_packet, total_energy_consumption))
    lockPrintResult.release()


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
        #print('Sender thread: sending a packet')
        eventNewPacketSecuPAN.set()
        eventNewPacketContiki.set()
        time.sleep(packet_sending_interval)
    print('Sender thread: sender thread ended')

def receiverContikiEx(hopToHopDelay, totalNumerOfHop, fragmentSendingEnergy, packetSize, fragmentSize, totalNumberOfFragment,simulation_time, attack_interval):
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
        #print("Receiver Thread (Contiki): waiting for packet to arrive")
        eventNewPacketContiki.clear()  # need to take care the position of the .clear method
        eventNewPacketContiki.wait()
        #print("Receiver Thread (Contiki): packet received")
        totalTimeForRecivingPackets += endtoEndDelay
        totalEnergyConsumptionForReceivingPackets += energyConsumptionForSendingPacket
        totalNumberOfReceivedPackets += 1

        lockAttackContiki.acquire()
        if attackFlagContiki:
            attackFlagContiki = 0
            lockAttackContiki.release()
            #print("Receiver Thread (Contiki): attack occured")

            totalTimeForRecivingPackets += endtoEndDelay # delay for sending the entire parcekt (all the fragments of a packet)
            totalEnergyConsumptionForReceivingPackets += energyConsumptionForSendingPacket # energy consumption for sending all the fragments of the altered packet
            totalNumberOfAttacks += 1

            #print("Receiver Thread (Contiki): Going to sleep due to attack (Contiki)")
            sleep_duration = endtoEndDelay/(attack_interval/.5) #.5 sec is the base attack intervale. For 1 sec or 1.5 sec the sleep time decreases
            time.sleep(sleep_duration / 1000)
        else:
            lockAttackContiki.release()

    print ("Contiki -> Total Energy Consumption (%d), Total Received Packet (%d), Number of Retransmitted Packets (%d)" %(totalEnergyConsumptionForReceivingPackets, totalNumberOfReceivedPackets, totalNumberOfAttacks))
    #average_energy_consumption = totalEnergyConsumptionForReceivingPackets/ (totalNumberOfReceivedPackets + totalNumberOfAttacks)
    average_energy_consumption = totalEnergyConsumptionForReceivingPackets / totalNumberOfReceivedPackets
    print ("Contiki average energy consumption %d" %(average_energy_consumption))
    #printEnergyResult(simulation_time,attack_interval,"Contiki", "Mesh-under",totalNumberOfAttacks,energyConsumptionForSendingPacket,totalNumberOfAttacks*energyConsumptionForSendingPacket)
    #printSimulationOutcome ("Contiki", "Mesh-under", totalPacketSent, totalNumberOfReceivedPackets, totalTimeForRecivingPackets,totalNumberOfAttacks,totalEnergyConsumptionForReceivingPackets)

def receiverSecuPANEx(hopToHopDelay, totalNumerOfHop, fragmentSendingEnergy, packetSize, fragmentSize, totalNumberOfFragment, simulation_time, attack_interval):
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
        #print("Receiver Thread (SecuPAN): waiting for packet to arrive")
        eventNewPacketContiki.clear()  # need to take care the position of the .clear method
        eventNewPacketContiki.wait()
        #print("Receiver Thread (SecuPAN): packet received")
        totalTimeForRecivingPackets += endtoEndDelay
        totalEnergyConsumptionForReceivingPackets += energyConsumptionForSendingPacket
        totalNumberOfReceivedPackets += 1

        lockAttackSecuPAN.acquire()
        if attackFlagSecuPAN:
            attackFlagSecuPAN = 0
            lockAttackSecuPAN.release()
        #    print("Receiver Thread (SecuPAN): attack occured")

            totalTimeForRecivingPackets += hopToHopDelay # delay for sending the fabricated/altered fragment
            totalEnergyConsumptionForReceivingPackets += fragmentSendingEnergy # energy consumption for sending the altered fragment
            totalNumberOfAttacks += 1
            sleep_time = endtoEndDelay / attack_interval # sleep_time decreases as attack interval increases
        #    print("Receiver Thread (SecuPAN): Going to sleep due to attack (SecuPAN)")
            time.sleep(sleep_time / 1000)
        else:
            lockAttackSecuPAN.release()
    print ("SecuPAN -> Total Energy Consumption (%d), Total Received Packet (%d), Number of Retransmitted Packets (%d)" %(totalEnergyConsumptionForReceivingPackets, totalNumberOfReceivedPackets, totalNumberOfAttacks))
    #average_energy_consumption = totalEnergyConsumptionForReceivingPackets/ (totalNumberOfReceivedPackets + totalNumberOfAttacks)
    average_energy_consumption = totalEnergyConsumptionForReceivingPackets / totalNumberOfReceivedPackets
    print ("SecuPAN average energy consumption %d" %(average_energy_consumption))

    #printEnergyResult(simulation_time,attack_interval,"SecuPAN", "Mesh-under",totalNumberOfAttacks,fragmentSendingEnergy,totalNumberOfAttacks*fragmentSendingEnergy)
    #printSimulationOutcome ("SecuPAN", "Mesh-under", totalPacketSent, totalNumberOfReceivedPackets, totalTimeForRecivingPackets,totalNumberOfAttacks,totalEnergyConsumptionForReceivingPackets)


def attacker(attack_interval):
    print("Attacker Thread: Attacker thread started")
    global exitFlag
    global attackFlagContiki
    global attackFlagSecuPAN

    while exitFlag == 0:
        time.sleep(attack_interval)

        lockAttackContiki.acquire()
    #    print("Attacker Thread: preforming attack on Contiki")
        attackFlagContiki = 1
        lockAttackContiki.release()

        lockAttackSecuPAN.acquire()
    #    print("Attacker Thread: preforming attack on SecuPAN")
        attackFlagSecuPAN = 1
        lockAttackSecuPAN.release()

    print("Attacker Thread: Attacker thread ended")


hopToHopDelay = 58   # ms for mesh-under
totalNumerOfHop = 2  # total number of intermediate nodes including the receiving node

fragmentSendingEnergy = 15 #10 mj for mesh-under and 15 mj for route-over
packetSize = 128 # in bytes (128, 256, 512)

fragmentSize = 46 #29 # in bytes for mesh-under
totalNumberOfFragment = math.ceil(packetSize/fragmentSize)

arrPacketSize = [128, 256, 512] # packet size in bytes
arrAttackInterval = [.5, 1.0, 1.5] # attack interval 500, 1000, and 1500 ms

for atkinterval in arrAttackInterval:
    print("Attack Interval: %.2f" %(atkinterval))
    for psize in arrPacketSize:
        print ("Packet Size: %d" %psize)

        #global exitFlag
        #global attackFlagContiki
        #global attackFlagSecuPAN

        exitFlag= 0
        attackFlagContiki = 0
        attackFlagSecuPAN = 0

        totalNumberOfFragment = math.ceil(psize / fragmentSize)

        threads = []
        t = threading.Thread(target=sender, args=(packetSendingInterval,))
        threads.append(t)
        t.start()

        t = threading.Thread(target=receiverContikiEx, args=(
        hopToHopDelay, totalNumerOfHop, fragmentSendingEnergy, psize, fragmentSendingEnergy, totalNumberOfFragment,simulationTime, atkinterval,))
        threads.append(t)
        t.start()

        t = threading.Thread(target=receiverSecuPANEx, args=(hopToHopDelay, totalNumerOfHop, fragmentSendingEnergy, psize, fragmentSendingEnergy, totalNumberOfFragment, simulationTime, atkinterval,))
        threads.append(t)
        t.start()

        t = threading.Thread(target=attacker, args=(atkinterval,))
        threads.append(t)
        t.start()

        t = threading.Thread(target=controller, args=(simulationTime,))
        threads.append(t)
        t.start()

        for t in threads:
            t.join()

print ("All Done !!!")
