import socket, struct, select, sys, threading

server_socket = None
clients = {}  # key = client tcp socket | value = client udp socket (ip, port)


def connection_thread():
    global server_socket, clients

    select_socket_rlist = [server_socket]
    while True:
        # get all the sockets from which there is data to be read
        ready_list, _, _ = select.select(select_socket_rlist, [], [])
        # iterate through all the sockets
        for sock in ready_list:
            if sock == server_socket:
                print('A new client connected.')
                # the server socket is triggered only if a connection has been made
                client_socket, client_addr = sock.accept()
                # send the length of the clients dictionary
                client_socket.sendall(struct.pack('!I', len(clients)))
                # send all the clients to the newly connected client.
                for other_client in clients:
                    other_client_udp = clients[other_client]
                    client_socket.send(socket.inet_aton(other_client_udp[0]))
                    client_socket.send(struct.pack('!I', other_client_udp[1]))
                # Received udp ip/port from the newly connected client
                new_client = (
                    socket.inet_ntoa(client_socket.recv(4)),
                    struct.unpack('!I', client_socket.recv(4))[0]
                )

                # Send the new client notification to all the other clients
                for other_client_socket in clients:
                    other_client_socket.sendall(b'N')
                    other_client_socket.sendall(socket.inet_aton(new_client[0]))
                    other_client_socket.sendall(struct.pack('!I', new_client[1]))

                # Add the new client to the clients list and to the sockets read list.
                clients[client_socket] = new_client
                select_socket_rlist.append(client_socket)
            else:
                # if the server receives info from other sockets, it means that
                # that client could only disconnect.
                operation = sock.recv(1)
                if operation == b'L':
                    print('Client ' + str(clients[sock]) + " is leaving...")
                    sock.close()
                    deleted_socket = clients[sock]
                    clients.pop(sock)
                    select_socket_rlist.remove(sock)
                    for other_client_socket in clients:
                        other_client_socket.sendall(b'L')
                        other_client_socket.sendall(socket.inet_aton(deleted_socket[0]))
                        other_client_socket.sendall(struct.pack('!I', deleted_socket[1]))
                else:
                    print('Unknown operation code.')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Invalid arguments to start the server...")
        exit(0)
    server_socket = socket.create_server((sys.argv[1], int(sys.argv[2])))
    server_socket.listen(10)

    print('Listening for client connections...\n')
    threading.Thread(target=connection_thread, daemon=True,).start()
    while True:
        server_input = input().strip()
        if server_input == 'exit':
            print("Shutting down...")
            # Send info to all the other clients that the server has been shut down
            for client_socket in clients:
                client_socket.sendall(b'S')
            exit(0)

