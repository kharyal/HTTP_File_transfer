import os
import time

def send_files_shortlist(arg, file_list, s, depth):
    l = len(arg)
    if l == 1:
        for i in range(len(file_list)):
            for d in range(depth):
                print("   ", end ="")
                s.send("   ".encode())
            print("|--", end ="")
            s.send("|--".encode())
            print(file_list[i])
            s.send((file_list[i]+"\n").encode())
            
            if os.path.isdir(file_list[i]):
                send_files_shortlist(arg, os.listdir("./"+str(file_list[i])), s, depth+1)

        

def  ind_get(arg, s):
    if arg[0] == 'shortlist':
        file_list = os.listdir()
        send_files_shortlist(arg,file_list,s,0)
                