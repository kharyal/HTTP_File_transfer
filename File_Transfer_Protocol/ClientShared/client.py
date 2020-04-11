import socket
import tqdm
import os
from copy import deepcopy 

cache_sz = 5
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 9994
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
                    fdata = fdata + str(data.decode()[:-5])
                    # print(fdata)
                    break
                else:
                    fdata = fdata + str(data.decode())
            
            stats = fdata.split("   ")[-4:]
            stats = stats[0]+"   "+stats[1]+"   "+stats[2]+ "   "+stats[3]
            print(stats)

            downloaded_data = fdata[:len(fdata)-len(stats)-2]

        if arg[0] == 'udp':
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            address = ('', 10000)
            try:
                udp_sock.bind(address)
            except:
                print("Unable to receive through udp")
                exit()
            if client_socket.recv(1024).decode() == "ready_for_sending":
                client_socket.send("begin_download".encode())
            
            while True:
                data = udp_sock.recvfrom(1024*5)
                if str(data[0].decode()[-5:]) == "-|-|-":
                    fdata = fdata + str(data[0].decode()[:-5])
                    break
                fdata = fdata + str(data[0].decode())

            # print(fdata.split("   "))
            stats = fdata.split("   ")[-4:]
            stats = stats[0]+"   "+stats[1]+"   "+stats[2]+ "   "+stats[3]
            print(stats)

            downloaded_data = fdata[:len(fdata)-len(stats)-2]


        if os.path.isfile(arg[1]):
            print("File already exists")
            return fdata
        else:
            f = open(arg[1],'w')
            f.write(downloaded_data)
            f.close()
            return fdata

def cach_e(arg):
    if arg[0] == "verify":
        present_in_cache = False
        ch = open(".cache")
        lines_to_read = list(range(2*cache_sz+2))
        cache_info_lines = list(range(1,2*cache_sz+2))
        for position, line in enumerate(ch):
            if position in lines_to_read:
                if position in cache_info_lines:
                    if line.strip('\n') == arg[1]:
                        print("The file is present in cache... returning it from cache")
                        ch.close()
                        ch = open(".cache")
                        cache_data = ch.readlines()
                        read_lines = cache_data[position+1].strip('\n').split('-')
                        read_lines = list(map(int, read_lines))

                        fdata_lines = cache_data[read_lines[0]:read_lines[1]+1]
                        if os.path.isfile(arg[1]):
                            print("File already exists")
                        else:
                            f = open(arg[1],'w')
                            f.writelines(fdata_lines[:-1])
                            f.close()
                            print(fdata_lines[-1])

                        present_in_cache = True
                        break

        if present_in_cache == False:
            ch.close()
            command = "FileDownload tcp "+str(arg[1])
            client_socket.send(command.encode())
            fdata = download(command.split(" ")[1:])
            ch = open(".cache")
            cache_data = ch.readlines()
            ch.close()
            fcfs = []
            if len(cache_data)>0:
                fcfs = cache_data[0].strip('\n')
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
                    l = cache_data[i].split("-")
                    l = list(map(int, l))
                    l[0] = l[0] - no_lines_to_remove
                    l[1] = l[1] - no_lines_to_remove
                    # print(l[0],l[1])
                    l = list(map(str, l))
                    cache_data[i] = l[0]+"-"+l[1]+'\n'

                no_lines_to_write = len(fdata.split('\n'))
                total_lines = len(cache_data)
                new_entry_start = total_lines - no_lines_to_remove
                new_entry_end = new_entry_start + no_lines_to_write -1
                cache_data[2*fcfs[-1]+1] = arg[1]+'\n'
                cache_data[2*fcfs[-1]+2] = str(new_entry_start)+"-"+str(new_entry_end)+'\n'
                ent = fcfs.pop(-1)
                fcfs.insert(0,ent)
                fcfs = list(map(str, fcfs))
                fcfs_str = ""
                for s in fcfs:
                    fcfs_str = fcfs_str + " " + s
                fcfs_str = fcfs_str+'\n'
                cache_data[0] = fcfs_str

                for lin in range(lines_to_remove[1],lines_to_remove[0]-1, -1):
                    cache_data.pop(lin)
                
                ch = open(".cache",'w')
                ch.writelines(cache_data)
                ch.write(fdata+'\n')
                ch.close()
            
            elif len(fcfs)>0:
                no_lines_to_write = len(fdata.split('\n'))
                total_lines = len(cache_data)
                new_entry_start = total_lines
                new_entry_end = new_entry_start + no_lines_to_write - 1

                cache_data[2*len(fcfs)+1] = arg[1]+'\n'
                cache_data[2*len(fcfs)+2] = str(new_entry_start)+"-"+str(new_entry_end)+'\n'
                fcfs.insert(0,len(fcfs))
                fcfs = list(map(str, fcfs))
                fcfs_str = ""
                for s in fcfs:
                    fcfs_str = fcfs_str + " " + s
                fcfs_str = fcfs_str+'\n'
                cache_data[0] = fcfs_str

                ch = open(".cache",'w')
                ch.writelines(cache_data)
                ch.write(fdata+'\n')
                ch.close()

            else:
                cache_data = ['\n']*(2*cache_sz+1)
                total_lines = len(cache_data)
                new_entry_start = total_lines
                no_lines_to_write = len(fdata.split('\n')) - 1 
                new_entry_end = new_entry_start+no_lines_to_write

                cache_data[0] = '0 '+'\n'
                cache_data[1] = arg[1]+'\n'
                cache_data[2] = str(new_entry_start)+"-"+str(new_entry_end)+'\n'

                ch = open(".cache",'w')
                ch.writelines(cache_data)
                ch.write(fdata+'\n')
                ch.close()

    if arg[0] == "show":
        ch = open(".cache")
        cache_data = ch.readlines()
        for i in range(1,2*cache_sz+1,2):
            filename = cache_data[i].strip('\n')
            dataline = int(cache_data[i+1].strip('\n').split("-")[1])
            data = cache_data[dataline].split("   ")[-3]
            print(filename+"   "+data)

def explore_files(file_list, pwd):
    for file in file_list:
        print(pwd + " " + file)
        if os.path.isdir(file):
            explore_files(os.listdir(pwd + file + "/"),pwd + file + "/")

def show_client_files():
    file_list = os.listdir()
    explore_files(file_list, "./")

def upload(arg):
    if client_socket.recv(1024).decode() == "Ready":
        if len(arg)>=1:
            if os.path.isfile(arg[0]):
                f = open(arg[0])
                sz = os.stat(arg[0]).st_size
                progress = tqdm.tqdm(range(sz), f"Uploading {arg[0]}", unit="B", unit_scale=True, unit_divisor=1024, ascii=True)
                contents = f.read(1024*15)
                while len(contents)>0:
                    client_socket.send(contents.encode())
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
    elif command[0] == "Teardown":
        client_socket.close()
        exit()