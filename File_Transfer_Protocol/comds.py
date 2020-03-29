import os
import time

def send_files_shortlist(arg, file_list, s, pwd):
    l = len(arg)
    if l == 1:
        for i in range(len(file_list)):
            print(pwd+str(file_list[i]))
            s.send((pwd+file_list[i]+"\n").encode())
            
            if os.path.isdir(pwd+str(file_list[i])):
                send_files_shortlist(arg, os.listdir(pwd+str(file_list[i])), s, pwd+str(file_list[i])+'/')

    elif l == 3:
        for i in range(len(file_list)):
            print(file_list[i])
            s.send((file_list[i]+"\n").encode())
            if os.path.isdir(pwd+str(file_list[i])):
                send_files_shortlist(arg, os.listdir(pwd+str(file_list[i])), s, pwd+str(file_list[i])+'/')
        

def  ind_get(arg, s):
    if arg[0] == 'shortlist':
        file_list = os.listdir()
        send_files_shortlist(arg,file_list,s, "./")
                