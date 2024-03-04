import ipaddress
import re

from mininet.topo import Topo
from mininet.log import setLogLevel, info

class CustomTopology(Topo): 
    def __init__(self, log_level='info'): 
        super().__init__()
        # This gets filled in add_host and will contain a structure: 
        #'host_name'= {
        #    'host_name': hosts_name, 
        #    'host_ip': host_ip, 
        #}
        self.hosts_dictionary={}

        # This gets filled in add_switch and will contain a structure: 
        # 'switch_name': 'switch_name'
        self.switches_dictionary={}

        setLogLevel(log_level)
        

    def add_switch(self, switch_name: str): 

        if not isinstance(switch_name,str): 
            raise ValueError("Error in add_switch: switch_name should be a string.")

        new_switch=self.addSwitch(switch_name)
        self.switches_dictionary[switch_name]={'switch_name': new_switch}

        info('Created switch: {switch_name}\n')

    def add_host(self, host_name:str, host_ip:str):

        if not isinstance(host_name,str): 
            raise ValueError("Error in add_host: host_name should be a string.")

        if not isinstance(host_ip,str):
            raise ValueError("Error in add_host: host_ip should be a string.")
    
        #try:
        #    ip = ipaddress.ip_address(host_ip)
        #    info(f"{host_ip} is a valid IP address, while adding host.\n")
        #except ValueError:
        #    info(f"Error: {host_ip} is not a valid IP address, while adding host.\n")

        h = self.addHost(host_name, ip=host_ip)
        info(f"Added host: {host_name} with ip: {host_ip}\n")

        self.hosts_dictionary[host_name]={
            'host_name': host_name, 
            'host_ip': host_ip, 
        }
    
    def add_hosts(self, hosts: dict): 
        
        if not isinstance(hosts, dict): 
            raise ValueError("Error in add_hosts. Hosts should be a python dictionary, with host_names as keys and host_ips as values.") 

        for host_name, host_ip in hosts.items(): 
            self.add_host(host_name=host_name, host_ip=host_ip)    


    def add_direct_link_between_hosts(self, host_name1: str, host_name2: str, delay: str=None, bandwidth: int=None): 
        def validate_delay(delay: str) -> bool:
            # This regular expression matches strings that start with one or more digits followed by 'ms'
            pattern = r'^\d+ms$'
            if re.match(pattern, delay):
                return True
            else:
                return False

        if not isinstance(host_name1,str): 
            raise ValueError("Error in add_direct_link_between_hosts: host_name1 should be a string.")

        if not isinstance(host_name2,str):
            raise ValueError("Error in add_direct_link_between_hosts:  host_name2 should be a string.")

        if bandwidth is not None and not isinstance(bandwidth, int): 
            raise ValueError("Error in add_direct_link_between_hosts: bandwidth should be an integer.")

        if delay is not None and not validate_delay(delay): 
            raise ValueError("Error in add_direct_link_between_hosts: delay should be a string that follows this format 'Xms'")

        self.addLink(self.hosts_dictionary[host_name1]['host_name'],self.hosts_dictionary[host_name2]['host_name'], delay=delay, bw=bandwidth)

        info(f'Added link between host: {host_name1} and host {host_name2}, with delay {delay} and bandwidth {bandwidth}\n')
        

    def add_switch_link_for_host(self, host_name:str, switch_name: str, delay: str=None, bandwidth: int=None):

        def validate_delay(delay: str) -> bool:
            # This regular expression matches strings that start with one or more digits followed by 'ms'
            pattern = r'^\d+ms$'
            if re.match(pattern, delay):
                return True
            else:
                return False

        if not isinstance(host_name,str): 
            raise ValueError("Error in add_switch_link_for_host: host_name should be a string.")

        if not isinstance(switch_name,str):
            raise ValueError("Error in add_switch_link_for_host: switch_name should be a string.")

        if bandwidth is not None and not isinstance(bandwidth, int): 
            raise ValueError("Error in add_switch_link_for_host: bandwidth should be an integer.")

        if delay is not None and not validate_delay(delay): 
            raise ValueError("Error in add_switch_link_for_host: delay should be a string that follows this format 'Xms'")

        self.addLink(self.switches_dictionary[switch_name]['switch_name'],self.hosts_dictionary[host_name]['host_name'], delay=delay, bw=bandwidth)

        info(f'Added link between host: {host_name} and switch {switch_name}, with delay {delay} and bandwidth {bandwidth}\n')

        




