from netmiko import Netmiko
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoAuthenticationException, NetMikoTimeoutException
from datetime import date

import getpass
from pprint import pprint
import signal,os

from queue import Queue
import threading

#signal.signal(signal.SIGPIPE, signal.SIG_DFL)
#signal.signal(signal.SIGINT, signal.SIG_DFL)  

TFTP_SERVER = "10.137.79.40"
date = date.today()
filedate = date.strftime("%d.%m.%Y")
user = input("Enter your Username: ")
password = getpass.getpass()

ip_address_file = open('./networkips.txt')
ip_address = ip_address_file.read().splitlines()

num_threads = 8
enclosure_queue = Queue()
print_lock = threading.Lock()

#copy_command = "copy running-config tftp://"+TFTP_SERVER+"/"+hostname+"_"+filedate+".txt"

def deviceconnector(i,q):
    while True:
        print("{}: Waiting for IP address...".format(i))
        ip = q.get()
        print("{}: Acquired IP: {}".format(i,ip))

        device_dict = {
            'host': ip,
            'username': user,
            'password': password,
            'device_type': 'cisco_ios'
        }

        try:
            net_connect = Netmiko(**device_dict)
        except NetMikoTimeoutException:
            with print_lock:
                print("\n{}: ERROR: Connection to {} timed-out.\n".format(i,ip))
            q.task_done()
            continue
        except NetMikoAuthenticationException:
            with print_lock:
                print("\n{}: ERROR: Authenticaftion failed for {}. Stopping thread. \n".format(i,ip))
            q.task_done()
            #os.kill(os.getpid(), signal.SIGUSR1)
        
        result = net_connect.send_command("show run | in hostname")
        result = result.split()
        hostname = result[1]

        copy_command = "copy running-config tftp://"+TFTP_SERVER+"/"+hostname+"_"+filedate+".txt"

        output = net_connect.send_command(copy_command, expect_string=r'Address or name of remote host ')
        output += net_connect.send_command('\n', expect_string=r'Destination filename', delay_factor=2)
        output += net_connect.send_command('\n', expect_string=r'#', delay_factor=2)

        with print_lock:
            print("{}: Printing output...".format(i))
            pprint(output)

        net_connect.disconnect
        q.task_done()

def main():
    global ip_address
    for i in range(num_threads):
        thread = threading.Thread(target=deviceconnector, args=(i,enclosure_queue,))
        thread.setDaemon(True)
        thread.start()
    
    for ip_address in ip_address:
        enclosure_queue.put(ip_address)

    enclosure_queue.join()
    print("*** Script Complete")

if __name__ == '__main__':
    main()
