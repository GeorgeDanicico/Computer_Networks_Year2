import socket, pickle, struct, sys, select, threading, random

random.seed()

server_number = 0
guessing_tries = {}

def resetSrv():
    global server_number
    server_number = random.randint(1, 10000)
    print('Server number is ' + str(server_number))

def connection_thread():
    global guessing_tries
    socket_list = [server_socket]
    clients = {}
    
    
    while True:
        ready_list, _, _ = select.select(socket_list, [], [])
        
        for sock in ready_list:
            if sock == server_socket:
                client_socket, _ = sock.accept()
                msg = 'The nr of digits to be guessed are ' + str(len(str(server_number)))
                client_socket.sendall(msg.encode('utf-8'))
                new_client = (
                    socket.inet_ntoa(client_socket.recv(4)),
                    struct.unpack('!I', client_socket.recv(4))[0]
                )

                print('Client ' + str(new_client) + " has joined the guessing game.")

                clients[client_socket] = new_client
                guessing_tries[client_socket] = ['_'] * len(str(server_number))
                socket_list.append(client_socket)
            else:
                operation = sock.recv(1)
                if operation == b'G':
                    digit = struct.unpack('!I', sock.recv(4))[0]
                    
                    nr = str(server_number)
                    array_of_positions = []
                    
                    for d in range(len(nr)):
                        if int(nr[d]) == digit and guessing_tries[sock][d] == '_':
                            guessing_tries[sock][d] = str(digit)
                    
                    print('Client ' + str(clients[sock]) + " said " + str(digit))
                    
                    if '_' not in guessing_tries[sock]:
                        print('Client ' + str(clients[sock]) + ' has guessed the number')
                        msg = 'Congratulations, you guessed the number: ' + str(server_number)
                        server_udp.sendto(msg.encode('utf-8'), clients[sock])
                                
                        for client in clients:
                            if client != sock:
                                server_udp.sendto('Too bad, someone else guessed the number.\n'.encode('utf-8'), clients[client])

                        print('Server shutting down...')
                        exit()
                    else:
                        pickled_array = pickle.dumps(guessing_tries[sock])
                        sock.send(struct.pack('!I', len(pickled_array)))
                        sock.sendall(pickled_array)


if __name__ == "__main__":
    server_socket = socket.create_server(('127.0.0.1', 1234))
    server_socket.listen(10)
    
    server_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    server_udp.bind(('0.0.0.0', 2500))
    
    print('listening for incoming connections...\n')
    
    resetSrv()
    threading.Thread(target=connection_thread).start()
    
    