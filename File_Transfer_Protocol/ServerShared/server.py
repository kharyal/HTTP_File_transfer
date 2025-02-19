import socket
import time
import os
import comds

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()

port = 9990
server_socket.bind((host, port))

server_socket.listen(5)

print('server listening...')

if not os.path.isfile("./.indexlog"):
            os.mknod(".indexlog")

indf = open(".indexlog", 'a')

while True:
    client_socket, addr = server_socket.accept()
    connected = True
    print('got connection from ' + str(addr))

    while connected == True:
        data = client_socket.recv(1024)
        if not data:
            connected = False
            break
        print('$> ' + data.decode())
        command = str(data.decode()).split(" ")

        if command[0] == "IndexGet":
            indf.write(data.decode() + "\n")
            comds.ind_get(command[1:],client_socket)
            client_socket.send("-|-|-".encode())

        if command[0] == "FileHash":
            comds.file_hash(command[1:],client_socket)
            client_socket.send("-|-|-".encode())

        if command[0] == "FileDownload":
            comds.file_download(command[1:],client_socket)
            if command[1] == "tcp":
                client_socket.send("-|-|-".encode())

        if command[0] == "FileUpload":
            comds.file_upload(command[1:], client_socket)

    print("connection Lost")
    client_socket.close()

