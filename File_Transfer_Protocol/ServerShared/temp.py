import os

f = open('logfile','r')
logs = f.readlines()
initial_details = os.stat('logfile')
initial_mtime = initial_details.st_mtime

print(f[-10:]) ## page refresh 


##assuming file is saved after every log entry
##and log file is not deleted 
while(1):
    current_details = os.stat('logfile')
    current_mtime = current_details.st_mtime
    if(current_mtime != initial_mtime):
        f_new = open('logfile','r')
        print(f_new[-1])
        

