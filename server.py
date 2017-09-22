# echo_server.py

import socketserver,time

clientInfo = dict()
clientbufferInfo = dict()
reAssemblyBuffer = 1024
class MyTCPSocketHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        global reAssemblyBuffer
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        client_info = self.data.decode("utf-8").split(',')

        if client_info[0] == 'attacker':
            reAssemblyBuffer=reAssemblyBuffer-32
        else:
            if reAssemblyBuffer < 32:
                time.sleep(1)
                self.request.sendall(bytes("dropped","utf-8"))
            else:
                time.sleep(1)
                self.request.sendall(bytes("recieved","utf-8"))

        #if client_info[0] not in clientInfo:
        #    clientInfo[client_info[0]] = client_info[1]
        #    reAssemblyBuffer=reAssemblyBuffer-8
        #else:
        #    clientbufferInfo[client_info[0]] = clientbufferInfo[client_info[0]] - 1
        # just send back the same data, but upper-cased
        #self.request.sendall(self.data.upper())
        #print(clientInfo)

if __name__ == "__main__":
    
    reAssemblyBuffer = 1024
    HOST, PORT = "localhost", 9999

    # instantiate the server, and bind to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPSocketHandler)

    # activate the server
    # this will keep running until Ctrl-C
    server.serve_forever()