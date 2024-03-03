import ipaddress

from mininet.topo import Topo

class Topology(Topo): 
    def __init__(self): 
        # This gets filled in add_host and will contain a structure: 
        #'host_name'= {
        #    'host_name': hosts_name, 
        #    'host_ip': host_ip, 
        #    'host_object': h
        #}
        self.hosts_dictionary={}

        # This gets filled in add_switch and will contain a structure: 
        # 'switch_name': 'switch_object'
        self.switches_dictionary={}

    def add_switch(switch_name: str): 

        if not isinstance(switch_name,str): 
            raise ValueError("Error in add_switch: switch_name should be a string.")

        new_switch=self.add_switch(switch_name)
        self.switch[switch_name]=new_switch

    def add_host(host_name:str, host_ip:str):

        if not isinstance(host_name,str): 
            raise ValueError("Error in add_host: host_name should be a string.")

        if not isinstance(host_ip,str):
            raise ValueError("Error in add_host: host_ip should be a string.")
    
        try:
            ip = ipaddress.ip_address(host_ip)
            print(f"{host_ip} is a valid IP address, while adding host.")
        except ValueError:
            print(f"Error: {host_ip} is not a valid IP address, while adding host.")

        h = self.addHost(host_name, ip=host_ip)
        print(f"Added host: {host_name} with ip: {host_ip}")

        self.hosts_dictionary[host_name]=
        {
            'host_name': hosts_name, 
            'host_ip': host_ip, 
            'host_object': h
        }
    
    def add_hosts(hosts: dict): 
        
        if not isinstance(hosts, dict): 
            raise ValueError("Error in add_hosts. Hosts should be a python dictionary, with host_names as keys and host_ips as values.") 

        for host_name, host_ip in hosts.items(): 
            self.add_host(host_name=host_name, host_ip=host_ip)    




