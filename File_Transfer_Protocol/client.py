import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 9991
client_socket.connect((host, port))


while True:
    cmd = input()
    client_socket.send(cmd.encode())
    # client_socket.close()
    
