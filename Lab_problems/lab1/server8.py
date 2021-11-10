import socket, pickle, struct

if __name__ == "__main__":
    server_socket = socket.create_server(('127.0.0.1', 1234))
    server_socket.listen(10)
    
    cs, caddr = server_socket.accept()
    print('Client connected')
    length = struct.unpack('!I', cs.recv(4))[0]
    array1 = pickle.loads(cs.recv(length))
    
    length = struct.unpack('!I', cs.recv(4))[0]
    array2 = pickle.loads(cs.recv(length))
    
    result = []
    
    for elem in array1:
        try:
            if array2.index(elem) != -1:
                result.append(elem)
        except ValueError:
            pass
    
    result_serialized = pickle.dumps(result)
    
    cs.send(result_serialized)
    
    print('Server closing...')