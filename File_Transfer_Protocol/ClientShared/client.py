import socket
import tqdm
import os

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 9992
client_socket.connect((host, port))

def get_data():
    while True:
        data = client_socket.recv(1024)    
        # print(str(data.decode()[-5:])=="-|-|-")
        if str(data.decode()[-5:]) == "-|-|-":
            # print(str(data.decode()))
            print(str(data.decode()[:-5]))
            break
        print(str(data.decode()), end = "")

def download(arg):
    fdata = ""
    if len(arg) >= 2:
        if arg[0] == 'tcp':
            while True:
                data = client_socket.recv(1024)
                if str(data.decode()[-5:]) == "-|-|-":
                    print(str(data.decode()[:-5]))
                    fdata = fdata + str(data.decode()[:-5])
                    # print(fdata)
                    break
                else:
                    fdata = fdata + str(data.decode())
            
            stats = fdata.split("  ")[-4:]
            stats = stats[0]+"  "+stats[1]+"  "+stats[2]+ "  "+stats[3]
            print(stats)

            downloaded_data = fdata[:len(fdata)-len(stats)]

        
        if os.path.isfile(arg[1]):
            print("File already exists")
            return
        else:
            f = open(arg[1],'w')
            f.write(downloaded_data)
            f.close

while True:
    print("$> ", end = " ")
    cmd = str(input())
    client_socket.send(cmd.encode())
    # client_socket.close()

    command = cmd.split(" ")
    if command[0] == "IndexGet":
        get_data()
    elif command[0] == "FileHash":
        get_data()
    elif command[0] == "FileDownload":
        download(command[1:])
    elif command[0] == "Teardown":
        client_socket.close()
        exit()