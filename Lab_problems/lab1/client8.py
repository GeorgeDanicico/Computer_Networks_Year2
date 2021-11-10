import pickle, struct, socket

if __name__ == "__main__":
    l1 = 4
    array1 = [1, 2, 3, 4]
    l2 = 4
    array2 = [1, 2, 4, 5]
    
    client_socket = socket.create_connection(('127.0.0.1', 1234))
    array1_serialized = pickle.dumps(array1)
    array2_serialized = pickle.dumps(array2)
    
    client_socket.send(struct.pack('!I', len(array1_serialized)))
    client_socket.sendall(array1_serialized)
    
    client_socket.send(struct.pack('!I', len(array2_serialized)))
    client_socket.sendall(array2_serialized)

    result = pickle.loads(client_socket.recv(1024))
    
    print('Common elements: ' + str(result))
    