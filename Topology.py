import re
import logging
import os
from typing import List

from mininet.topo import Topo
from mininet.log import MininetLogger
from mininet.node import Host



# Define a new logging format
standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

_logger = MininetLogger(os.path.basename(__file__))
#TODO hardcoded log level
_logger.setLogLevel('debug')
for handler in _logger.handlers:
    handler.setFormatter(logging.Formatter(standard_logging))


class CustomTopology(Topo): 
    def __init__(self): 
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

        # Get filled in add_mininet_hosts when minindn is created
        # 'host.name': 'mininethost object'
        self.mininet_hosts = {}


    def run_command_on_mininet_host(self, host_name:str, command:str, verbose: bool=True) -> str:
        _logger.info(f"Running command: {command} on host: {host_name}\n")
        host = self.mininet_hosts.get(host_name, None) 

        if host is None: 
            _logger.error(f"Host {host_name} is not found in mininet_hosts\n")
            return '' 

        result = host.cmdPrint(command)
        _logger.debug(f"Result after running: {command} on host: {host_name}\nResult: {result}\n")

        return result

    def add_mininet_hosts(self, hosts: List[Host]): 
        #TODO compatibility between topo and hosts
        for host in hosts: 
            #call topo hosts method which returns hosts as a list
            if host.name not in self.hosts(): 
                raise ValueError(f"Error in add_mininet_hosts. Host {host.name} is not present in {self.hosts}")

            _logger.debug(f"Adding mininet host: {host.name} to self.mininet_hosts dictionary\n")
            self.mininet_hosts[host.name] = host

    def add_switch(self, switch_name: str): 

        if not isinstance(switch_name, str): 
            raise ValueError("Error in add_switch: switch_name should be a string.")

        new_switch=self.addSwitch(switch_name)
        self.switches_dictionary[switch_name]={'switch_name': new_switch}

        _logger.info(f'Created switch: {switch_name}\n')

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
        _logger.info(f"Added host: {host_name} with ip: {host_ip}\n")

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

        _logger.info(f'Added link between host: {host_name1} and host {host_name2}, with delay {delay} and bandwidth {bandwidth}\n')
        

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

        _logger.info(f'Added link between host: {host_name} and switch {switch_name}, with delay {delay} and bandwidth {bandwidth}\n')

        




