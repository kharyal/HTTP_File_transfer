import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 9990
client_socket.connect((host, port))

def ind_get(arg):
    while True:
        data = client_socket.recv(1024)    
        # print(str(data.decode()[-5:])=="-|-|-")
        if str(data.decode()[-5:]) == "-|-|-":
            print(str(data.decode()[:-5]))
            break
        print(str(data.decode()), end = "")


while True:
    print("$> ", end = " ")
    cmd = str(input())
    client_socket.send(cmd.encode())
    # client_socket.close()

    command = cmd.split(" ")
    if command[0] == "IndexGet":
        ind_get(command[0:])
    
    if command[0] == "Teardown":
        client_socket.close()
        exit()