import socket, threading, struct, sys, select, random

clients = {}
random.seed()
mutex_lock = threading.Lock()
server_number = 0

def resetSrv():
    global server_number
    server_number = random.randint(0, 100)
    print(f'The server number is: {server_number}')

def connection():
    global clients, server_number, mutex_lock
    socket_list = [server_socket]
    
    while True:
        rlist, _, _ = select.select(socket_list, [], [])
        
        for sock in rlist:
            if sock == server_socket:
                client_socket, _ = sock.accept()
                client_socket.sendall(struct.pack('!I', len(clients)))
                
                for other_client in clients:
                    other_client_udp = clients[other_client]
                    client_socket.send(socket.inet_aton(other_client_udp[0]))
                    client_socket.send(struct.pack('!I', other_client_udp[1]))

                new_client = (
                    socket.inet_ntoa(client_socket.recv(4)),
                    struct.unpack('!I', client_socket.recv(4))[0]
                )
                
                print('Client ' + str(new_client) + " has joined the guessing game.")

                for other_client_socket in clients:
                    other_client_socket.sendall(b'N')
                    other_client_socket.sendall(socket.inet_aton(new_client[0]))
                    other_client_socket.sendall(struct.pack('!I', new_client[1]))

                clients[client_socket] = new_client
                socket_list.append(client_socket)
            else:
                operation = sock.recv(1)
                if operation == b'L':
                    print('Client ' + str(clients[sock]) + " is leaving...")
                    sock.close()
                    deleted_socket = clients[sock]
                    clients.pop(sock)
                    socket_list.remove(sock)
                    for other_client_socket in clients:
                        other_client_socket.sendall(b'L')
                        other_client_socket.sendall(socket.inet_aton(deleted_socket[0]))
                        other_client_socket.sendall(struct.pack('!I', deleted_socket[1]))
                elif operation == b'G':
                    guess = struct.unpack('!I', sock.recv(4))[0]
                    if guess != server_number:
                        sock.send(b'F')
                        sock.sendall('Too bad, try again!'.encode('utf-8'))
                    else:
                        mutex_lock.acquire()
                        sock.send(b'G')
                        print('Client ' + str(clients[sock]) + ' has guessed the number')
                        msg = 'Congratulations, you guessed the number: ' + str(guess)
                        sock.sendall(msg.encode('utf-8'))
                        
                        for client in clients:
                            if client != sock:
                                client.send(b'F')
                                client.sendall('Too bad, someone else guessed the number.\n'.encode('utf-8'))

                        resetSrv()
                        for client in clients:
                            client.sendall('A new round has started. Good luck.'.encode('utf-8'))

                        mutex_lock.release()
                    
if __name__ == "__main__":
    # the ip and the port are command line arguments
    if len(sys.argv) != 3:
        print("IP/PORT")
        exit(-1)
        
    try:
        server_socket = socket.create_server((sys.argv[1], int(sys.argv[2])))
    except socket.error as msg:
        print(msg.strerror)
        exit(-1)
        
    server_socket.listen(20)
    threading.Thread(target=connection, daemon=True,).start()
    print('Listening for incoming connections...\n')
    
    resetSrv()
    
    while True:
        comm = input()
        if comm == 'quit':
            print('Shutting down...')
            for client_socket in clients:
                client_socket.sendall(b'S')
            # server_socket.close()
            exit(-1)
            