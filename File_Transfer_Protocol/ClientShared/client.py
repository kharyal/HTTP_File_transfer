import socket
import tqdm
import os
from copy import deepcopy 

cache_sz = 5
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 9991
client_socket.connect((host, port))

def get_data():
    invalid_args = False
    while True:
        data = client_socket.recv(1024)
        if str(data.decode()[:7]) == "inv_fil":
            print("#### Invalid Arguments ####")
            invalid_args = True
        
        if str(data.decode()[-5:]) == "-|-|-":
            # print(str(data.decode()))
            if invalid_args == False:
                print(str(data.decode()[:-5]))
            break
        
        if invalid_args == False:
            print(str(data.decode()), end = "")

def download(arg):
    fdata = b''
    invalid_file = False
    if len(arg) >= 2:
        if arg[0] == 'tcp':
            while True:
                data = client_socket.recv(1024)
                if data[:len("inv_fil".encode())] == "inv_fil".encode():
                    print("File doesnt exist")
                    invalid_file = True
                
                if data[-1*len("-|-|-".encode()):] == "-|-|-".encode():
                    if not invalid_file:
                        fdata = fdata + data[:-1*len("-|-|-".encode())]
                    # print(fdata)
                    break
                else:
                    if not invalid_file:
                        fdata = fdata + data
            if not invalid_file:
                print("File downloaded, ready to write...")

            if not invalid_file:
                stats = fdata.split("   ".encode())[-4:]
                stats = str(stats[0].decode())+"   "+str(stats[1].decode())+"   "+str(stats[2].decode())+ "   "+str(stats[3].decode())
                print(stats)
                downloaded_data = fdata[:len(fdata)-len(stats.encode())-2]

        if arg[0] == 'udp':
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            address = ('', 10000)
            try:
                udp_sock.bind(address)
            except:
                print("Unable to receive through udp")
                exit()
            if client_socket.recv(1024).decode() == "ready_for_sending":
                client_socket.send("send_sz".encode())
            read_sz = client_socket.recv(1024).decode()

            if read_sz == "inv_file":
                read_sz = 0
            else:
                read_sz = int(read_sz)

            client_socket.send("begin_download".encode())
            
            data = udp_sock.recvfrom(1024*15)
            while len(fdata)<read_sz:
                # data = udp_sock.recvfrom(1024*5)
                if data[0][:len("inv_fil".encode())] == "inv_fil".encode():
                    print("File doesnt exist")
                    invalid_file = True
                
                if not invalid_file:
                    fdata = fdata + data[0]
                    break
                data = udp_sock.recvfrom(1024*15)

            if not invalid_file:
                print("File downloaded, ready to write...")
            #     udp_sock.close()


            if not invalid_file:
                # print(fdata.split("   "))
                # stats = fdata.split("   ".encode())[-4:]
                # stats = str(stats[0].decode())+"   "+str(stats[1].decode())+"   "+str(stats[2].decode())+ "   "+str(stats[3].decode())
                # print(stats)
                stats = client_socket.recv(1024)
                stats = stats.decode()
                print(stats)
                downloaded_data = fdata
                # downloaded_data = fdata[:len(fdata)-len(stats)-2]

        if os.path.isfile(arg[1]):
            print("File already exists")
            return fdata, invalid_file
        else:
            if not invalid_file:
                pth = arg[1].split("/")
                if pth[0] == '.':
                    pth.pop(0)
                pa_th = "./"
                for diridx in range(len(pth)-1):
                   pa_th = pa_th+"/"+pth[diridx]
                   os.mkdir(pa_th) 

                os.mknod(arg[1])
                f = open(arg[1],'wb')
                f.write(downloaded_data)
                f.close()
            return fdata, invalid_file

def cach_e(arg):
    if arg[0] == "verify":
        present_in_cache = False
        if not os.path.isfile("./.cache"):
            os.mknod(".cache")
        ch = open(".cache", 'rb')
        lines_to_read = list(range(2*cache_sz+1))
        cache_info_lines = list(range(1,2*cache_sz+1))
        lines = ch.readlines()
        for position in range(len(lines)):
            if position in lines_to_read:
                if position in cache_info_lines:
                    if lines[position].strip('\n'.encode()).decode() == arg[1]:
                        print("The file is present in cache... returning it from cache")
                        ch.close()
                        ch = open(".cache",'rb')
                        cache_data = ch.readlines()
                        read_lines = cache_data[position+1].decode().strip('\n').split('-')
                        read_lines = list(map(int, read_lines))
                        

                        fdata_lines = cache_data[read_lines[0]:read_lines[1]+1]
                        if os.path.isfile(arg[1]):
                            print("File already exists")
                        else:
                            pth = arg[1].split("/")
                            if pth[0] == '.':
                                pth.pop(0)
                            pa_th = "./"
                            for diridx in range(len(pth)-1):
                               pa_th = pa_th+"/"+pth[diridx]
                               os.mkdir(pa_th) 

                            os.mknod(arg[1])
                            f = open(arg[1],'wb')
                            f.writelines(fdata_lines[:-1])
                            f.close()
                            # print(fdata_lines)
                            print(fdata_lines[-1].decode())

                        present_in_cache = True
                        break

        if present_in_cache == False:
            ch.close()
            command = "FileDownload tcp "+str(arg[1])
            client_socket.send(command.encode())
            fdata, invalid_file = download(command.split(" ")[1:])

            if not invalid_file:
                ch = open(".cache", 'rb')
                cache_data = ch.readlines()
                ch.close()
                fcfs = []
                if len(cache_data)>0:
                    fcfs = cache_data[0].strip('\n'.encode()).decode()
                    fcfs = fcfs.split(" ")
                    for i in range(len(fcfs)-1,-1,-1):
                        if fcfs[i] == '' or fcfs[i] == ' ':
                            fcfs.pop(i)

                    # print(fcfs)
                    fcfs = list(map(int, fcfs))
                if len(fcfs)>=cache_sz:
                    lines_to_remove = cache_data[2*fcfs[-1]+2].strip('\n').split("-")
                    lines_to_remove = list(map(int, lines_to_remove))
                    no_lines_to_remove = lines_to_remove[1]-lines_to_remove[0]+1
                    l = []
                    for i in range(2,2*cache_sz+1,2):
                        l = deepcopy(l)
                        l = cache_data[i].decode().split("-")
                        l = list(map(int, l))
                        l[0] = l[0] - no_lines_to_remove
                        l[1] = l[1] - no_lines_to_remove
                        # print(l[0],l[1])
                        l = list(map(str, l))
                        cache_data[i] = (l[0]+"-"+l[1]+'\n').encode()

                    no_lines_to_write = len(fdata.split('\n'.encode()))
                    total_lines = len(cache_data)
                    new_entry_start = total_lines - no_lines_to_remove
                    new_entry_end = new_entry_start + no_lines_to_write -1
                    cache_data[2*fcfs[-1]+1] = (arg[1]+'\n').encode()
                    cache_data[2*fcfs[-1]+2] = (str(new_entry_start)+"-"+str(new_entry_end)+'\n').encode()
                    ent = fcfs.pop(-1)
                    fcfs.insert(0,ent)
                    fcfs = list(map(str, fcfs))
                    fcfs_str = ""
                    for s in fcfs:
                        fcfs_str = fcfs_str + " " + s
                    fcfs_str = fcfs_str+'\n'
                    cache_data[0] = fcfs_str.encode()

                    for lin in range(lines_to_remove[1],lines_to_remove[0]-1, -1):
                        cache_data.pop(lin)

                    ch = open(".cache",'wb')
                    ch.writelines(cache_data)
                    ch.close()
                    ch = open(".cache", 'ab')
                    # lins = ch.readlines()
                    # ch.writelines(lins)
                    ch.write(fdata+"\n".encode())
                    ch.close()

                elif len(fcfs)>0:
                    no_lines_to_write = len(fdata.split('\n'.encode()))
                    total_lines = len(cache_data)
                    new_entry_start = total_lines
                    new_entry_end = new_entry_start + no_lines_to_write - 1

                    cache_data[2*len(fcfs)+1] = (arg[1]+'\n').encode()
                    cache_data[2*len(fcfs)+2] = (str(new_entry_start)+"-"+str(new_entry_end)+'\n').encode()
                    fcfs.insert(0,len(fcfs))
                    fcfs = list(map(str, fcfs))
                    fcfs_str = ""
                    for s in fcfs:
                        fcfs_str = fcfs_str + " " + s
                    fcfs_str = fcfs_str+'\n'
                    cache_data[0] = fcfs_str.encode()

                    ch = open(".cache",'wb')
                    ch.writelines(cache_data)
                    ch.close()
                    ch = open(".cache", 'ab')
                    # lins = ch.readlines()
                    # ch.writelines(lins)
                    ch.write(fdata+"\n".encode())
                    ch.close()

                else:
                    cache_data = ['\n'.encode()]*(2*cache_sz+1)
                    total_lines = len(cache_data)
                    new_entry_start = total_lines
                    no_lines_to_write = len(fdata.split('\n'.encode())) - 1 
                    new_entry_end = new_entry_start+no_lines_to_write

                    cache_data[0] = ('0 '+'\n').encode()
                    cache_data[1] = (arg[1]+'\n').encode()
                    cache_data[2] = (str(new_entry_start)+"-"+str(new_entry_end)+'\n').encode()

                    ch = open(".cache",'wb')
                    ch.writelines(cache_data)
                    ch.close()
                    ch = open(".cache", 'ab')
                    # lins = ch.readlines()
                    # ch.writelines(lins)
                    ch.write(fdata+"\n".encode())
                    ch.close()

    if arg[0] == "show":
        ch = open(".cache" ,'rb')
        cache_data = ch.readlines()
        fcfs = []
        if len(cache_data)>0:
            fcfs = cache_data[0].strip('\n'.encode()).decode()
            fcfs = fcfs.split(" ")
            for i in range(len(fcfs)-1,-1,-1):
                if fcfs[i] == '' or fcfs[i] == ' ':
                    fcfs.pop(i)
            fcfs = list(map(int, fcfs))
        size_occupied = len(fcfs)

        for i in range(1,2*size_occupied+1,2):
            filename = cache_data[i].decode().strip('\n')
            dataline = int(cache_data[i+1].decode().strip('\n').split("-")[1])
            data = cache_data[dataline].decode().split("   ")[-3]
            print(filename+"   "+data)

def explore_files(file_list, pwd):
    for file in file_list:
        print(pwd + file)
        if os.path.isdir(file):
            explore_files(os.listdir(pwd + file + "/"),pwd + file + "/")

def show_client_files():
    file_list = os.listdir()
    explore_files(file_list, "./")

def upload(arg):
    if client_socket.recv(1024).decode() == "Ready":
        if len(arg)>=1:
            if os.path.isfile(arg[0]):
                f = open(arg[0], 'rb')
                sz = os.stat(arg[0]).st_size
                progress = tqdm.tqdm(range(sz), f"Uploading {arg[0]}", unit="B", unit_scale=True, unit_divisor=1024, ascii=True)
                contents = f.read(1024*15)
                while len(contents)>0:
                    client_socket.send(contents)
                    progress.update(len(contents))
                    contents = f.read(1024*15)
                client_socket.send("-|-|-".encode())
            else:
                print("File doesn't exist")
        else:
            print("Not enough arguments")



while True:
    print("$> ", end = " ")
    cmd = str(input())
    command = cmd.split(" ")
    if command[0] != "Caching":
        client_socket.send(cmd.encode())
    # client_socket.close()

    if command[0] == "IndexGet":
        get_data()
    elif command[0] == "FileHash":
        get_data()
    elif command[0] == "FileDownload":
        download(command[1:])
    elif command[0] == "Caching":
        cach_e(command[1:])
    elif command[0] == "MyFiles":
        show_client_files()
    elif command [0] == "FileUpload":
        upload(command[1:])
    elif command[0] == "Teardown" or command[0] == "teardown":
        client_socket.close()
        exit()
    else:
        print("Invalid command")