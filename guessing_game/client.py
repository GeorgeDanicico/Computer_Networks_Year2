import socket, threading, struct, sys, select

other_clients = set()
client_TCP_socket = None
client_UDP_socket = None

def connection():
    global client_UDP_socket, client_TCP_socket, other_clients

    # listen for incoming messages from the tcp_server or from the other clients
    while True:
        sockets, _, _ = select.select([client_TCP_socket, client_UDP_socket], [], [])

        if client_TCP_socket in sockets:
            operation = client_TCP_socket.recv(1)  # This can be N - new client or L - a client has left.
            
            if operation != b'':
                if operation == b'L':
                    ipaddress = socket.inet_ntoa(client_TCP_socket.recv(4))
                    port = struct.unpack("!I", client_TCP_socket.recv(4))[0]
                    print("Client " + ipaddress + ":" + str(port) + " left the guessing game.")
                    other_clients.discard((ipaddress, port))
                elif operation == b'N':
                    ipaddress = socket.inet_ntoa(client_TCP_socket.recv(4))
                    port = struct.unpack("!I", client_TCP_socket.recv(4))[0]
                    print("Client " + ipaddress + ":" + str(port) + " has joined the guessing game.")
                    other_clients.add((ipaddress, port))
                elif operation == b'S':
                    print('The server has been shut down.')
                    exit(-1)
                elif operation == b'F' or operation == b'R' or operation == b'G':
                    message = client_TCP_socket.recv(1024).decode('utf-8')
                    print(message)
                    
                else:
                    print('Unknown command received from the server')
                    
        if client_UDP_socket in sockets:
            message, address = client_UDP_socket.recvfrom(256)
            print("Client " + address[0] + ":" + str(address[1]) + " -> " + message.decode('utf-8'))


if __name__ == "__main__":
    # the ip and the port are command line arguments
    if len(sys.argv) != 4:
        print("IP/PORT/UDP PORT not given.")
        exit(-1)
        
    try:
        client_TCP_socket = socket.create_connection((sys.argv[1], int(sys.argv[2])))
    except socket.error as msg:
        print(msg.strerror)
        exit(-1)
        
    number_of_clients = struct.unpack('!I', client_TCP_socket.recv(4))[0]
    for _ in range(number_of_clients):
        other_clients.add((
            socket.inet_ntoa(client_TCP_socket.recv(4)),
            struct.unpack('!I', client_TCP_socket.recv(4))[0]
        ))
        
    client_UDP_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    client_UDP_socket.bind(('0.0.0.0', int(sys.argv[3])))

    udp_ip, udp_port = client_UDP_socket.getsockname()
    print("My UDP address is " + udp_ip + ":" + str(udp_port))
    # We will send the udp_ip and the udp_port to the server to update the clients list.
    client_TCP_socket.send(socket.inet_aton(udp_ip))
    client_TCP_socket.send(struct.pack('!I', udp_port))

    print('Currently online clients: ')
    if len(other_clients) == 0:
        print('none\n')
    else:
        for client in other_clients:
            print('Client ' + str(client))
        print('\n')
        
    threading.Thread(target=connection, daemon=True,).start()
    
    while True:
        my_guess = input()
        if my_guess == 'quit':
            client_TCP_socket.send(b'L')
            print('Exiting the game and shutting down...')
            # client_TCP_socket.close()
            exit(0)
        try:
            my_guess = int(my_guess)
            client_TCP_socket.send(b'G')
            client_TCP_socket.send(struct.pack('!I', my_guess))

            message = 'Client ' + str((udp_ip, udp_port)) + " said " + str(my_guess)
            for client in other_clients:
                client_UDP_socket.sendto(message.encode('utf-8'), client)
        except ValueError as err:
            print("Invalid value given.")
            exit(-1)