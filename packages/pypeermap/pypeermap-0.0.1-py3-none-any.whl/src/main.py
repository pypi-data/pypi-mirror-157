import os 
import socket
import subprocess

from black import main

class pypeermap:
    def get_my_ip(self):
        return socket.gethostbyname(socket.gethostname())
    
    def calculate_scan_range(self,ip):
        return ip.rsplit('.', 1)[0]+".0/24"

    def perform_scan(self,range):
        proc = subprocess.Popen(["nmap -sn "+ range], stdout=subprocess.PIPE, shell=True)
        (out, _) = proc.communicate()
        return out 

    def get_ip_list(self,nmap_out):
        key_string = "Nmap scan report for "
        val =  str(nmap_out).split('\\n')[2:]
        return [i.replace(key_string, '').split(' ') for i in val if key_string in i]

    def full_process(self):
        ip = self.get_my_ip()
        range = self.calculate_scan_range(ip)
        nmap_out = self.perform_scan(range)
        ip_list = self.get_ip_list(nmap_out)
        return ip_list

if __name__ == "__main__":
    peermap = pypeermap()
    print(peermap.full_process())