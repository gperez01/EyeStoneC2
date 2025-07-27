
# EyeStoneC2 - Command & Control framework
# Copyright (C) 2025 Gabriel Pérez Navarro

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

#!/usr/bin/env python3

import os
import sys
import socket
import threading

from server.agent import AgentManager

class AgentHandler:

    def __init__(self, agent_socket, agent_address):

        self.agent_socket = agent_socket
        self.agent_ip = agent_address[0]
        self.agent_port = agent_address[1]
        self.agent_sysinfo = self.get_agent_sysinfo()

    def __str__(self):

        return f"\n[+] IPv4: {self.agent_ip}\n[+] RPORT: {self.agent_port}\n[+] System information: {self.print_sysinfo()}"


    def get_agent_sysinfo(self):

        self.agent_socket.sendall("getinfo:system".encode())
        bytestream = self.agent_socket.recv(4096)

        bytes_list = bytestream.split(b'\x00')

        output_list = []
        for element in bytes_list:
            element = element.decode()
            if element != '':
                output_list.append(element)

        return output_list


    def interact(self):

        print("\n[...] Interacting with agent, type 'exit' to finish agent interaction\n")

        prompt = f"[{self.agent_ip}] >> "

        while True:

            try:

                command = input(prompt)
                
                if command == "exit":

                    print("\n")

                    break

                self.agent_socket.sendall(command.encode())

                response = self.agent_socket.recv(8192)

                if response.decode() == 'output:none':

                    print("\n")

                else:

                    print("\n" + response.decode())

            except (ConnectionResetError, BrokenPipeError, OSError):

                print("[!] ERROR: Connection lost...")

                self.agent_socket.close()

                break


    def send_file(self, src_path, dst_path):

        print(f"[{self.agent_ip}] - File transfer started...")

        self.agent_socket.sendall("data:download".encode())

        if self.agent_socket.recv(1024).decode() == "download:req:path":

            self.agent_socket.sendall(dst_path.encode())

            if self.agent_socket.recv(1024).decode() == "download:req:data":

                with open(src_path, 'rb') as src_file:

                    src_data =  src_file.read()

                    self.agent_socket.sendall(src_data)

                agent_response = self.agent_socket.recv(1024).decode()

                if agent_response == "download:ok":

                    print(f"[{self.agent_ip}] - File transfer completed")

                else:

                    print(f"[{self.agent_ip}] - File transfer failed. Agent response: {agent_response}")
                


    def execute_file(self, command_file):

        print(f"[{self.agent_ip}] - Execution started...")

        self.agent_socket.sendall("data:command_file".encode())

        if self.agent_socket.recv(1024).decode() == "command_file:req:commands":

            with open(command_file, 'rb') as command_file:

                command_data = command_file.read()

                self.agent_socket.sendall(command_data)

            agent_response = self.agent_socket.recv(1024).decode()

            if agent_response == "command_file:exec:success":

                print(f"[{self.agent_ip}] - Execution completed")

            else:

                print(f"[{self.agent_ip}] - Execution failed. Agent response: {agent_response}")


            

    def print_sysinfo(self):
        return f'''

{'System Name':<15}: {self.agent_sysinfo[0]}
{'Node Name':<15}: {self.agent_sysinfo[1]}
{'Release':<15}: {self.agent_sysinfo[2]}
{'Version':<15}: {self.agent_sysinfo[3]}
{'Architecture':<15}: {self.agent_sysinfo[4]}
{'Domain':<15}: {self.agent_sysinfo[5]}

    '''

