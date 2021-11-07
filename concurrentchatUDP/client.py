import socket
import threading
import sys
import time

msgOnConnection = " \0"
serverAddressPort = None
serverAddress = None
UDPClientSocket = None
finished = False


def receiveFromServer(UDPSocket):
    global finished
    while not finished:
        data = UDPSocket.recvfrom(1024)
        message = data[0].decode('ascii')
        if message == 'exit':
            finished = True
            break
        print(message)
        time.sleep(0.1)


if __name__ == '__main__':
    arguments = sys.argv
    if len(arguments) != 3:
        print("Invalid number of arguments")
        exit(-1)

    try:
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        serverAddressPort = (arguments[1], int(arguments[2]))
        serverAddress = arguments[1]
    except socket.error as msg:
        print("Error: ", msg.strerror)
        exit(-1)

    t = threading.Thread(target=receiveFromServer, args=(UDPClientSocket,), daemon=True)
    t.start()

    while not finished:
        clientMsg = input("")
        if (clientMsg == 'exit'):
            finished = True
        UDPClientSocket.sendto(clientMsg.encode('ascii'), serverAddressPort)

    print("You've disconnected from the chat.")
    t.join()
