import threading, socket, select, struct, sys

other_clients = set()

def connection_thread():
    select_rlist = [client_TCP_socket, client_UDP_socket]
    
    while True:
        read_list, _, _ = select.select(select_rlist, [], [])
        
        if client_TCP_socket in read_list:
            operation = client_TCP_socket.recv(1)
            if operation != b'':
                new_client_ip = socket.inet_ntoa(client_TCP_socket.recv(4))
                new_client_port = struct.unpack('!I', client_TCP_socket.recv(4))[0]
                
                if operation == b'N':
                    other_clients.add((
                        new_client_ip,
                        new_client_port
                    ))
                    print('Client ' + new_client_ip + ":" + str(new_client_port) + " has connected to the chatroom.")
                elif operation == b'L':
                    other_clients.discard((
                        new_client_ip,
                        new_client_port
                    ))
                    print('Client ' + new_client_ip + ":" + str(new_client_port) + " has left the chatroom.")
                    
        if client_UDP_socket in read_list:
            message, client_addr = client_UDP_socket.recvfrom(1024)
            print('Client ' + client_addr[0] + ':' + str(client_addr[1]) + " -> " + message.decode('utf-8'))
                    

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Invalid arguments given...")
        exit(-1)
    
    try:    
        client_TCP_socket = socket.create_connection((sys.argv[1], int(sys.argv[2])))
    except socket.error as msg:
        print(msg.strerror)
        exit(-1)
    
    # get the clients from the server
    number_of_clients = struct.unpack('!I', client_TCP_socket.recv(4))[0]  # length of the clients list
    for _ in range(number_of_clients):
        other_clients.add(
            (
                socket.inet_ntoa(client_TCP_socket.recv(4)),  # convert the address 
                struct.unpack('!I', client_TCP_socket.recv(4))[0]  # received the port
            )
        )
    
    # CREATE THE UDP SOCKET FOR THE CURRENT CLIENT
    client_UDP_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    client_UDP_socket.bind(('localhost', int(sys.argv[3])))
    # GET INFO ABOUT THE UDP IP/PORT
    udp_ip, udp_port = client_UDP_socket.getsockname()
    
    # send client udp ip/port to the server
    client_TCP_socket.sendall(socket.inet_aton(udp_ip))
    client_TCP_socket.sendall(struct.pack('!I', udp_port))
    
    threading.Thread(target=connection_thread, daemon=True).start()
    
    while True:
        user_msg = input()
        if user_msg == 'quit':
            client_TCP_socket.send(b'L')
            print("Shutting down and leaving the chatroom.")
            exit(0)
            
        for client in other_clients:
            client_UDP_socket.sendto(user_msg.encode('utf-8'), client)