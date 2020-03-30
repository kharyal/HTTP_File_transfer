import os
import time
import datetime

def find_file_type(filename):
    name_dict = {
        '.txt':'Text', '.pdf':'PDF', '.py':'Python', '.jpg':'Image',
        '.jpeg':'Image', '.png':'Image', '.sh':'Bash', '.pyc':'Python-cache'
    }
    for ext in list(name_dict.keys()):
        if filename.endswith(ext):
            return name_dict[ext]
    return "Directory"

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
        

def  ind_get(arg, s):
    if arg[0] == 'shortlist':
        file_list = os.listdir()
        send_files_shortlist(arg,file_list,s, "./")

if __name__=="__main__":
    ind_get(['shortlist','30:Mar:2020:00:00:00','30:Mar:2020:10:00:00'],'s')
