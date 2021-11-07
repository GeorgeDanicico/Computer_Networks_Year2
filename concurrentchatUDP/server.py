import socket
import threading
import sys

clientsAddresses = []
serverAddressPort = None
serverAddress = None
UDPServerSocket = None

def sendMessageFromServer():
    global clientsAddresses, UDPServerSocket

    while True:
        serverMessage = input("")

        serverMessage = "Server: " + serverMessage
        for client in clientsAddresses:
            UDPServerSocket.sendto(serverMessage.encode('ascii'), client)


def sendClientMessageToOthers(clientAddr, message):
    global clientsAddresses, UDPServerSocket

    for client in clientsAddresses:
        if client != clientAddr:
            UDPServerSocket.sendto(message.encode('ascii'), client)


if __name__ == '__main__':

    cmd = sys.argv
    if len(cmd) != 3:
        print("Invalid arguments to start the server")
    try:
        UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serverAddressPort = (cmd[1], int(cmd[2]))
        serverAddress = cmd[1]
        UDPServerSocket.bind(serverAddressPort)
    except socket.error as msg:
        print(msg.strerror)
        exit(-1)

    t = threading.Thread(target=sendMessageFromServer, daemon=True)
    t.start()
    print('Listening for connections...\n')

    while True:
        data = UDPServerSocket.recvfrom(1024)
        clientAddress = data[1]
        if clientAddress not in clientsAddresses:
            print('Client ' + clientAddress[0] + ' has connected to the chat.')
            clientsAddresses.append(clientAddress)

        clientMessage = data[0].decode('ascii')
        if clientMessage == 'exit':
            clientMessage = 'Client ' + str(data[1]) + ' has disconnected from the chat.'
            UDPServerSocket.sendto('exit'.encode('ascii'), clientAddress)  # ensure that the client execution will stop.
            clientsAddresses.remove(clientAddress)  # remove the client that has exited from the clients list
        else:
            clientMessage = 'Client ' + str(data[1]) + ': ' + data[0].decode('ascii')
        sendClientMessageToOthers(clientAddress, clientMessage)
        print(clientMessage)
