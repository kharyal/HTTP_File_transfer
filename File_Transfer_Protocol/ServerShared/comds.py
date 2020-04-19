import os
import time
import datetime
import hashlib
import tqdm
import socket

###### General functions that can be used anywhere ######
def find_file_type(filename):
    name_dict = {
        '.txt':'Text', '.pdf':'PDF', '.py':'Python', '.jpg':'Image',
        '.jpeg':'Image', '.png':'Image', '.sh':'Bash', '.pyc':'Python-cache'
    }
    for ext in list(name_dict.keys()):
        if filename.endswith(ext):
            return name_dict[ext]
    return "Directory"

###### Functions for IndexGet command ######
def send_files_shortlist(arg, file_list, s, pwd):
    mon_dict = {
        'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6,
        'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12
    }
    l = len(arg)
    if l == 1:
        for i in range(len(file_list)):
            print(pwd+str(file_list[i]))
            s.send((pwd+file_list[i]+"\n").encode())
            
            if os.path.isdir(pwd+str(file_list[i])):
                send_files_shortlist(arg, os.listdir(pwd+str(file_list[i])), s, pwd+str(file_list[i])+'/')

    elif l >= 3:
        start_date = int(arg[1].split(":")[0])
        start_month = mon_dict[arg[1].split(":")[1]]
        start_year = int(arg[1].split(":")[2])
        start_time_hrs = int(arg[1].split(":")[3])
        start_time_min = int(arg[1].split(":")[4])
        start_time_sec = int(arg[1].split(":")[5])

        end_date = int(arg[2].split(":")[0])
        end_month = mon_dict[arg[2].split(":")[1]]
        end_year = int(arg[2].split(":")[2])
        end_time_hrs = int(arg[2].split(":")[3])
        end_time_min = int(arg[2].split(":")[4])
        end_time_sec = int(arg[2].split(":")[5])

        st_d = datetime.date(start_year, start_month, start_date)
        end_d = datetime.date(end_year, end_month, end_date)
        st_t = datetime.time(start_time_hrs, start_time_min, start_time_sec)
        end_t = datetime.time(end_time_hrs, end_time_min, end_time_sec)

        for f in file_list:
            st = os.stat(pwd+str(f))
            tim = time.ctime(st.st_ctime).split(" ")
            for t in range(len(tim)-1,-1,-1):
                if tim[t] == "" or tim[t] == " ":
                    tim.pop(t)

            month = mon_dict[tim[1]]
            date = int(tim[2])
            time_hrs = int(tim[3].split(":")[0])
            time_min = int(tim[3].split(":")[1])
            time_sec = int(tim[3].split(":")[2])
            year = int(tim[4])
            sz = str(st.st_size)
            typ = find_file_type(pwd+str(f))
            if l>3 and not (pwd+str(f)).endswith(arg[3][1:]):
                if os.path.isdir(pwd+str(f)):
                    send_files_shortlist(arg, os.listdir(pwd+str(f)), s, pwd+str(f)+'/')
                continue

            d = datetime.date(year, month, date)
            if d>=st_d and d<=end_d:
                tim = datetime.time(time_hrs, time_min, time_sec)
                if tim>=st_t and tim<end_t:
                    print(pwd+str(f))
                    s.send((pwd+str(f)+"   "+str(date)+ ":" + str(month) + ":" 
                    + str(year) + ":" + str(time_hrs) + ":" + str(time_min)+
                    ":" + str(time_sec)+ "    " + sz + "   " + typ +"\n").encode())
                    if os.path.isdir(pwd+str(f)):
                        send_files_shortlist(arg, os.listdir(pwd+str(f)), s, pwd+str(f)+'/')


def send_files_longlist(arg, file_list, s, pwd):
    mon_dict = {
        'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6,
        'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12
    }
    l = len(arg)
    for f in file_list:
        st = os.stat(pwd+str(f))
        tim = time.ctime(st.st_ctime).split(" ")
        for t in range(len(tim)-1,-1,-1):
            if tim[t] == "" or tim[t] == " ":
                tim.pop(t)
                

        month = mon_dict[tim[1]]
        date = int(tim[2])
        time_hrs = int(tim[3].split(":")[0])
        time_min = int(tim[3].split(":")[1])
        time_sec = int(tim[3].split(":")[2])
        year = int(tim[4])
        sz = str(st.st_size)
        tim = datetime.time(time_hrs, time_min, time_sec)
        typ = find_file_type(pwd+str(f))
        
        if l>1 and not (pwd+str(f)).endswith(arg[1][1:]):
            if os.path.isdir(pwd+str(f)):
                send_files_longlist(arg, os.listdir(pwd+str(f)), s, pwd+str(f)+'/')
            continue
        
        if l<=2:
            print(pwd+str(f))

            s.send((pwd+str(f)+"   "+str(date)+ ":" + str(month) + ":" 
            + str(year) + ":" + str(time_hrs) + ":" + str(time_min)+
            ":" + str(time_sec)+ "    " + sz + "   " + typ +"\n").encode())
        elif l>2:            
            if os.path.isfile(pwd+f):
                with open(pwd+f) as file:
                    contents = file.read()
                    if arg[2] in contents:
                        print(pwd+f)
                        s.send((pwd+str(f)+"   "+str(date)+ ":" + str(month) + ":" 
                        + str(year) + ":" + str(time_hrs) + ":" + str(time_min)+
                        ":" + str(time_sec)+ "    " + sz + "   " + typ +"\n").encode())

        if os.path.isdir(pwd+str(f)):
            send_files_longlist(arg, os.listdir(pwd+str(f)), s, pwd+str(f)+'/')


def  ind_get(arg, s):
    if arg[0] == 'shortlist':
        file_list = os.listdir()
        send_files_shortlist(arg,file_list,s, "./")

    elif arg[0] == 'longlist':
        file_list = os.listdir()
        send_files_longlist(arg, file_list, s, "./")

    else:
        s.send("inv_arg".encode())

###### Functions for Hashfile command ######
def verify_md5(filename, s, with_file_size = False):
    md5 = hashlib.md5()
    fil = open(filename)
    contents = fil.read(1024*15)
    while len(contents)>0:
        md5.update(contents.encode())
        contents = fil.read(1024*15)

    if os.path.isfile(filename):
        st = os.stat(filename)
        tim = time.ctime(st.st_mtime).split(" ")
        date = tim[2]
        month = tim[1]
        year = tim[4]
        timst = tim[3]
        date_and_time = date+":"+month+":"+year+":"+timst
        if not with_file_size:
            print(filename+"   "+date_and_time+"   "+md5.hexdigest())
            s.send((filename+"   "+date_and_time+"   "+md5.hexdigest()+"\n").encode())
        else:
            sz = st.st_size
            print(filename+"   "+str(sz)+"   "+date_and_time+"   "+md5.hexdigest())
            s.send((filename+"   "+str(sz)+"   "+date_and_time+"   "+md5.hexdigest()).encode())

def check_all(file_list,s, pwd):
    for f in file_list:
        if os.path.isdir(pwd+f):
            check_all(os.listdir(pwd+f), s, pwd+f+"/")
            continue
        if f.endswith('.pyc'):
            continue
        verify_md5(pwd+f,s)

def file_hash(arg, s):
    if arg[0] == 'verify':
        if os.path.isfile(arg[1]):
            verify_md5(arg[1],s)
        else:
            print(arg[1] + " " + "File doesn't exist")
            s.send((arg[1] + " " + "File doesn't exist").encode())
    
    elif arg[0] == 'checkall':
        file_list = os.listdir('./')
        check_all(file_list, s, './')

    else:
        s.send("inv_arg".encode())

###### Functions for FileDownload command ######
def send_tcp(filename,s):
    if os.path.isfile(filename):
        f = open(filename)
        sz = os.stat(filename).st_size
        progress = tqdm.tqdm(range(sz), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024, ascii=True)
        contents = f.read(1024*15)
        while len(contents)>0:
            s.send(contents.encode())
            progress.update(len(contents))
            contents = f.read(1024*15)
        s.send("   ".encode())
        verify_md5(filename, s, with_file_size=True)
    else:
        print("File doesn't exist")
        s.send("inv_fil".encode())

def send_udp(filename,s):
    s.send("ready_for_sending".encode())
    if s.recv(1024).decode()[-14:] == "begin_download":
        if os.path.isfile(filename):
            md5 = hashlib.md5()
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            address = ('', 10000)
            f = open(filename)
            sz = os.stat(filename).st_size

            progress = tqdm.tqdm(range(sz), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024, ascii=True)
            contents = f.read(1024*15)
            while len(contents)>0:
                to_send = contents.encode()
                udp_socket.sendto(to_send,address)
                md5.update(contents.encode())
                progress.update(len(contents))
                contents = f.read(1024*15)

            st = os.stat(filename)
            tim = time.ctime(st.st_mtime).split(" ")
            date = tim[2]
            month = tim[1]
            year = tim[4]
            timst = tim[3]
            date_and_time = date+":"+month+":"+year+":"+timst
            sz = st.st_size
            print(filename+"   "+str(sz)+"   "+date_and_time+"   "+md5.hexdigest())
            udp_socket.sendto(("   "+filename+"   "+str(sz)+"   "+date_and_time+"   "+md5.hexdigest()).encode(),address)
            udp_socket.sendto("-|-|-".encode(), address)
        else:
            print("File doesn't exist")
            s.send("inv_fil".encode())
            s.send("-|-|-".encode())

def file_download(arg,s):
    if len(arg)>=2:
        if arg[0] == 'tcp':
            send_tcp(arg[1],s)
        
        elif arg[0] == 'udp':
            send_udp(arg[1],s)

        else:
            s.send("inv_arg".encode())

def file_upload(arg,s):
    fdata = ""
    s.send("Ready".encode())
    while True:
        data = s.recv(1024)
        if str(data.decode()[-5:]) == "-|-|-":
            fdata = fdata + str(data.decode()[:-5])
            # print(fdata)
            break
        else:
            fdata = fdata + str(data.decode())
    
    if os.path.isfile(arg[0]):
        print("File already exists")
    else:
        f = open(arg[0],'w')
        f.write(fdata)
        f.close()


if __name__=="__main__":
    file_download(['tcp', 'shared2.txt'],'s')
