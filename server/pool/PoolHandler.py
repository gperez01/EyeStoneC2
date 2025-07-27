
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

import threading

class PoolHandler():

    def __init__(self, name):

        self.name = name
        self.agent_list = []


    def add_agent(self, agent):

        self.agent_list.append(agent)

        print(f"[+] Agent added to pool '{self.name}' successfully!")


    def remove_agent(self, agent_id):

        del self.agent_list[agent_id - 1]

        print(f"[+] Agent removed from pool '{self.name}' successfully!")
        print("[+] The agent is still active but it does not belong to this pool anymore.")


    def list_agents(self):

        print(f"\nListing Agents inside pool '{self.name}':\n")
        print(f"{'ID':<15}{'IPv4':<15}{'Port':<15}{'Node Name':<15}{'OS':<15}")
        print("="*80 + "\n")

        ctr = 1

        for agent in self.agent_list:

            print(f"{ctr:<15}{agent.agent_ip:<15}{agent.agent_port:<15}{agent.agent_sysinfo[1]:<15}{agent.agent_sysinfo[0]:<15}")
            ctr += 1

        print("\n" + "="*80 + "\n")


    def send_file(self, src_path, dst_path):

        transfer_threads = []

        print(f"\n[+] Starting file transfers - Target pool: '{self.name}'\n")

        for agent in self.agent_list:

            transfer_thread = threading.Thread(target=agent.send_file, args=(src_path, dst_path))

            transfer_threads.append(transfer_thread)

        for transfer_thread in transfer_threads:

            transfer_thread.start()

        for transfer_thread in transfer_threads:

            transfer_thread.join()

        print(f"\n[+] All file transfers finished.\n")


    def execute_file(self, command_file):

        execute_threads = []

        print(f"\n[+] Starting command execution - Target pool: '{self.name}'\n")

        for agent in self.agent_list:

            execute_thread = threading.Thread(target=agent.execute_file, args=(command_file,))

            execute_threads.append(execute_thread)

        for execute_thread in execute_threads:

            execute_thread.start()

        for execute_thread in execute_threads:

            execute_thread.join()

        print(f"\n[+] Execution finished on all agents.\n")


 
    



        
