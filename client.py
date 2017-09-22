# echo_client.py

import socket, sys,time

packet_sent = 0
packet_delivered = 0
HOST, PORT = "localhost", 9999
client = sys.argv[1]
data = " ".join(sys.argv[2:])
print('data ='+data)

# create a TCP socket
t1 = time.clock()
t2 = time.clock()

while True:
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
	    # connect to server 
	    sock.connect((HOST, PORT))

	    # send data
	    sock.sendall(bytes(client+","+data + "\n","utf-8"))

	    # receive data back from the server
	    received = str(sock.recv(1024),"utf-8")
	    packet_sent += 1
	finally:
	    # shut down
	    sock.close()

	if received == "recieved":
		packet_delivered += 1

	print(packet_delivered/packet_sent)
	print("Sent:     {}".format(data))
	print("Received: {}".format(received))
	t2 = time.clock()