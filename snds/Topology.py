import sys
import configparser
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
    def __init__(
        self,
        extra_host_options: dict=None,
        extra_link_options: dict=None,
        extra_switch_options: dict=None,
    ):
        super().__init__(hopts=extra_host_options, lopts=extra_link_options, sopts=extra_switch_options)
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

        # Gets filled in add_port
        self.all_ports_dictionary = {}
        
        # Map edge nodes to IP addresses
        self.edge_nodes = {}


    def run_command_on_mininet_host(self, host_name:str, command:str, verbose: bool=True) -> str:
        _logger.info(f"Running command: {command} on host: {host_name}\n")
        host = self.mininet_hosts.get(host_name, None)

        #if host is None:
        #    _logger.error(f"Host {host_name} is not found in mininet_hosts\n")
        #    return ''

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

    def add_port(self, src: str, dst: str, src_port: None, dest_port: None):

        self.addPort(src=src, dst=dst, sport=src_port, dport=dest_port)

        self.all_ports_dictionary[f"{src}-{dst}-{src_port}-{dest_port}"] = {"src": src, "dst": dst, "src_port": src_port, "dest_port": dest_port}

        _logger.info(f'Created port: {self.all_ports_dictionary[f"{src}-{dst}-{src_port}-{dest_port}"]}\n')


    def add_switch(self, switch_name: str, **kwargs):

        if not isinstance(switch_name, str):
            raise ValueError("Error in add_switch: switch_name should be a string.")

        new_switch=self.addSwitch(switch_name, **kwargs)
        self.switches_dictionary[switch_name]={'switch_name': new_switch}

        _logger.info(f'Created switch: {switch_name}\n')

    def add_host(self, host_name:str, **kwargs):

        self.addHost(name=host_name, **kwargs)

        _logger.info(f"Added host: {host_name} \n")

        self.hosts_dictionary[host_name]={
            'host_name': host_name,
        }

    def add_link(self, node1: str, node2: str, port1=None, port2=None, **kwargs):

        self.addLink(node1=node1, node2=node2, port1=port1, port2=port2, **kwargs)

        _logger.info(f'Added link between host: {node1} and host {node2}\n')


    def processTopo(self, topoFile: str):
        _logger.info(f"Reading topoFile: {topoFile}\n")
        config = configparser.ConfigParser(delimiters=' ', allow_no_value=True)
        config.read(topoFile)

        items = config.items('nodes')
        _logger.debug(f"Read nodes from topoFile: {items}\n")
        coordinates = []

        for item in items:
            name = item[0].split(':')[0]
            params = {}
            if item[1]:
                if all (x in item[1] for x in ['radius', 'angle']) and item[1] in coordinates:
                    _logger.error("FATAL: Duplicate Coordinate, \'{}\' used by multiple nodes\n" \
                        .format(item[1]))
                    sys.exit(1)
                coordinates.append(item[1])

                for param in item[1].split(' '):
                    if param == '_':
                        continue
                    params[param.split('=')[0]] = param.split('=')[1]

            self.add_host(name, params=params)

            _logger.debug(f"Added host: {name} with params: {params}\n")

        try:
            items = config.items('switches')
            _logger.debug(f"Read switches from topoFile: {items}\n")
            for item in items:
                name = item[0].split(':')[0]
                self.add_switch(name)
                _logger.debug(f"Added switch: {name}\n")
        except configparser.NoSectionError:
            # Switches are optional
            pass

        items = config.items('links')
        _logger.debug(f"Read links from topoFile: {items}")
        for item in items:
            link = item[0].split(':')

            params = {}
            for param in item[1].split(' '):
                key = param.split('=')[0]
                value = param.split('=')[1]
                if key in ['jitter', 'max_queue_size']:
                    value = int(value)
                if key == 'loss' or key == 'bw':
                    value = float(value)
                params[key] = value

            self.add_link(link[0], link[1], **params)

            _logger.debug(f"Added link: {link}\n")

        faces = {}
        try:
            items = config.items('faces')
            _logger.debug(f"Read faces from topoFile: {items}")
            for item in items:
                face_a, face_b = item[0].split(':')
                _logger.debug(f"Read face from file {item}\n")
                cost = -1
                for param in item[1].split(' '):
                    if param.split("=")[0] == 'cost':
                        cost = param.split("=")[1]
                face_info = (face_b, int(cost))
                if face_a not in faces:
                    faces[face_a] = [face_info]
                else:
                    faces[face_a].append(face_info)
        except configparser.NoSectionError:
            _logger.debug("Faces section is optional\n")
            pass
        _logger.info("Succesfully read topoFile\n")
        return (self, faces)


