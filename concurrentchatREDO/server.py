import threading, socket, select, struct, sys

def connection_thread():
    clients = {}
    read_sockets = [server_socket]
    
    while True:
        rlist, _, _ = select.select(read_sockets, [], [])
        
        for sock in rlist:
            if sock == server_socket:
                client_socket, client_addr = sock.accept()
                print('Client ' + client_addr[0] + ':' + str(client_addr[1]) + 'has connected to the chat.')
                client_socket.sendall(struct.pack('!I', len(clients)))
                for client in clients:
                    udp_info = clients[client]
                    client_socket.send(socket.inet_aton(udp_info[0]))
                    client_socket.send(struct.pack('!I', udp_info[1]))

                # receive udp info the new client
                client_udp_ip = socket.inet_ntoa(client_socket.recv(4))
                client_udp_port = struct.unpack('!I', client_socket.recv(4))[0]
            
                for client in clients:
                    client.sendall(b'N')
                    client.send(socket.inet_aton(client_udp_ip))
                    client.send(struct.pack('!I', client_udp_port))
                    
                read_sockets.append(client_socket)
                clients[client_socket] = (client_udp_ip, client_udp_port)
            else:
                deleted_socket = clients[sock]
                sock.close()
                clients.pop(sock)
                read_sockets.remove(sock)
                
                print("Client " + deleted_socket[0] + ":" + str(deleted_socket[1]) + " has left.")
                 
                for client in clients:
                    client.sendall(b'L')
                    client.send(socket.inet_aton(deleted_socket[0]))
                    client.send(struct.pack('!I', deleted_socket[1]))
                    

if __name__ == "__main__":
    
    try:    
        server_socket = socket.create_server(('127.0.0.1', 1234))
    except socket.error as msg:
        print(msg.strerror)
        exit(-1)
        
    print("Listening for incoming connections...\n")
    server_socket.listen(10)
    
    threading.Thread(target=connection_thread, daemon=True).start()
    
    while True:
        msg = input()
        if msg == 'quit':
            print("Shutting down the server...")
            exit(0)