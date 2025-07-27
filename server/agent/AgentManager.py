
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

import socket

class AgentManager():

    instance = None

    def __new__ (cls):

        if cls.instance is None:
            cls.instance = super(AgentManager, cls).__new__(cls)
            cls.instance.agents = []

        return cls.instance

    def add_agent(self, agent):

        self.agents.append(agent)


    def remove_agent(self, agent_id):

        try: 

            target_agent = self.agents[agent_id]

            target_agent.agent_socket.sendall('agent:remove'.encode())

            target_agent.agent_socket.shutdown(socket.SHUT_RDWR)
        
            target_agent.agent_socket.close()

            print(f"[!] Agent socket ({target_agent.agent_ip}:{target_agent.agent_port}) closed")

            del self.agents[agent_id]

            print("[!] Agent removed from agent list\n")

        except IndexError:

            print("Invalid index, please type 'list agents' to check the current active agents and their indexes")

        except OSError:

            del self.agents[agent_id]

            print("[WARNING] The socket assigned to this agent was already closed, but it was still present in the agent list.")
            print("[WARNING] Please check the agent state, as the connection was closed unexpectedly")



    def detach_agent(self, agent_id):

        try: 

            target_agent = self.agents[agent_id]

            target_agent.agent_socket.sendall('agent:detach'.encode())

            print("\n[!] Agent uninstalled from target machine")

            target_agent.agent_socket.shutdown(socket.SHUT_RDWR)
        
            target_agent.agent_socket.close()

            print(f"[!] Agent socket ({target_agent.agent_ip}:{target_agent.agent_port}) closed")

            del self.agents[agent_id]

            print("[!] Agent removed from agent list\n")

        except IndexError:

            print("Invalid index, please type 'list agents' to check the current active agents and their indexes")

        except OSError:

            del self.agents[agent_id]

            print("[WARNING] The socket assigned to this agent was already closed, but it was still present in the agent list.")
            print("[WARNING] Please check the agent state, as the connection was closed unexpectedly")

    
    def remove_all_agents(self):

        for target_agent in self.agents:

            try:

                target_agent.agent_socket.sendall('agent:remove'.encode())

                target_agent.agent_socket.shutdown(socket.SHUT_RDWR)

                target_agent.agent_socket.close()

                self.agents.remove(target_agent)

            except OSError:

                pass


    def list_agents(self):

        print("\nListing Agents:\n")
        print(f"{'ID':<15}{'IPv4':<15}{'Port':<15}{'Node Name':<15}{'OS':<15}")
        print("="*80 + "\n")

        ctr = 1

        for agent in self.agents:

            print(f"{ctr:<15}{agent.agent_ip:<15}{agent.agent_port:<15}{agent.agent_sysinfo[1]:<15}{agent.agent_sysinfo[0]:<15}")
            ctr += 1

        print("\n" + "="*80 + "\n")


    def interact_agent(self, agent_id):

        try:

            current_agent = self.agents[agent_id]

            current_agent.interact()

        except IndexError:

            print("Invalid index, please type 'list agents' to check the current active agents and their indexes")




    def get_agent(self, agent_id):

        try:

            return self.agents[agent_id]

        except IndexError:

            raise

    def send_file(self, agent_id, src_path, dst_path):

        try:

            target_agent = self.get_agent(agent_id)

            target_agent.send_file(src_path, dst_path)

        except IndexError:

            print("Invalid index, please type 'list agents' to check the current active agents and their indexes")
            


