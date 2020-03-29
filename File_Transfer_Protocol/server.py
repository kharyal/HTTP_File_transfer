import socket
import time

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()

port = 9991
server_socket.bind((host, port))

server_socket.listen(5)

print('server listening...')

while True:
    client_socket, addr = server_socket.accept()
    connected = True
    print('got connection from ' + str(addr))

    while connected == True:
        data = client_socket.recv(1024)
        if data.decode() == '':
            connected = False
            break
        print('Server recieved data: ' + data.decode())
    client_socket.close()