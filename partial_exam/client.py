import socket, pickle, struct, sys, select, threading, random, time

random.seed()
client_TCP_socket = None
client_UDP_socket = None
finished = False

def connection():
    global client_UDP_socket, client_TCP_socket, finished

    # listen for incoming messages from the tcp_server or from the other clients
    while True:
        sockets, _, _ = select.select([client_TCP_socket, client_UDP_socket], [], [])

        if client_TCP_socket in sockets:
            # check if there is a respone from the server ...
            response = client_TCP_socket.recv(4);
            if response:
                length = struct.unpack('!I', response)[0]
                array = client_TCP_socket.recv(length)
                array = pickle.loads(array)
                print(f'The positions you guessed until now are: {str(array)}')
            
        if client_UDP_socket in sockets:
            message, _ = client_UDP_socket.recvfrom(256)
            message = message.decode('utf-8')
            if 'Congratulations' in message:
                finished = True
            
            print(message)


if __name__ == "__main__":
    try:
        client_TCP_socket = socket.create_connection(('127.0.0.1', 1234))
    except socket.error as msg:
        print("Error")
        exit(-1)
    
    client_UDP_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    client_UDP_socket.bind(('0.0.0.0', int(sys.argv[1])))

    msg = client_TCP_socket.recv(1024).decode('utf-8')
    print(msg)

    udp_ip, udp_port = client_UDP_socket.getsockname()
    # We will send the udp_ip and the udp_port to the server to update the clients list.
    client_TCP_socket.send(socket.inet_aton(udp_ip))
    client_TCP_socket.send(struct.pack('!I', udp_port))
    
    threading.Thread(target=connection, daemon=True,).start()

    while not finished:
        my_guess = random.randint(0, 9)
        try:
            if not finished:
                client_TCP_socket.send(b'G')
                client_TCP_socket.send(struct.pack('!I', my_guess))
                time.sleep(1.2)
        except ValueError as err:
            print("Invalid value given.")
            exit(-1)