import socket, struct, select, sys, threading

client_TCP_socket = None  # the client will comunicate using the tcp socket with the server
client_UDP_socket = None  # the client will use the udp socket to communicate with the other clients.
other_clients = set()


def communication_thread():
    global client_UDP_socket, client_TCP_socket, other_clients

    # listen for incoming messages from the tcp_server or from the other clients
    while True:
        sockets, _, _ = select.select([client_TCP_socket, client_UDP_socket], [], [])

        if client_TCP_socket in sockets:
            operation = client_TCP_socket.recv(1)  # This can be N - new client or L - a client has left.
            if operation == b'L':
                ipaddress = socket.inet_ntoa(client_TCP_socket.recv(4))
                port = struct.unpack("!I", client_TCP_socket.recv(4))[0]
                print("Client " + ipaddress + ":" + str(port) + " left the chatroom.")
                other_clients.discard((ipaddress, port))
            elif operation == b'N':
                ipaddress = socket.inet_ntoa(client_TCP_socket.recv(4))
                port = struct.unpack("!I", client_TCP_socket.recv(4))[0]
                print("Client " + ipaddress + ":" + str(port) + " has joined the chatroom.")
                other_clients.add((ipaddress, port))
            elif operation == b'S':
                print('The server has been shut down.')
        if client_UDP_socket in sockets:
            message, address = client_UDP_socket.recvfrom(256)
            print("Client " + address[0] + ":" + str(address[1]) + " -> " + message.decode('utf-8'))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Invalid arguments given...")
        exit(-1)

    # Connect the client to the TCP client
    client_TCP_socket = socket.create_connection((sys.argv[1], int(sys.argv[2])))

    # Retrieve the list of current clients
    number_of_clients = struct.unpack('!I', client_TCP_socket.recv(4))[0]
    for _ in range(number_of_clients):
        other_clients.add((
            socket.inet_ntoa(client_TCP_socket.recv(4)),
            struct.unpack('!I', client_TCP_socket.recv(4))[0]
        ))

    # create the client UDP socket
    client_UDP_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # Since the client UDP socket does not have any port binded, we will send a random message
    # just to force the OS to assign a port
    client_UDP_socket.sendto(b'message', ('192.254.254.254', 24544))

    # Now we will get the port and the ip address pf the socket
    udp_ip, udp_port = client_UDP_socket.getsockname()
    print("My UDP address is " + udp_ip + ":" + str(udp_port))
    # We will send the udp_ip and the udp_port to the server to update the clients list.
    client_TCP_socket.send(socket.inet_aton(udp_ip))
    client_TCP_socket.send(struct.pack('!I', udp_port))

    print('Currently online clients: ')
    if len(other_clients) == 0:
        print('none')
    else:
        for client in other_clients:
            print('Client ' + str(client))
    # Start the thread that will handle incoming messages from the clients and the updates from the server.
    # daemon = True => the thread exits once the main thread stops
    threading.Thread(target=communication_thread, daemon=True).start()

    while True:
        # send user input to the other clients
        # send notification message to the server if the current client wants to leave.
        user_input = input()
        if user_input == 'exit':
            client_TCP_socket.sendall(b'L')
            print('Leaving the chat room...')
            exit(0)

        for client in other_clients:
            client_UDP_socket.sendto(user_input.encode('utf-8'), client)



