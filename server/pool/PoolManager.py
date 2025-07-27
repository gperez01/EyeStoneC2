
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

from server.pool import PoolHandler
from server.agent import AgentManager

class PoolManager():

    instance = None 

    def __new__ (cls):

        if cls.instance is None:
            cls.instance = super(PoolManager, cls).__new__(cls)
            cls.instance.pools = []

        return cls.instance

    def add_pool(self, pool):

        self.pools.append(pool)


    def delete_pool(self, pool_name):

        deleted = False

        for pool in self.pools:

            if pool.name == pool_name:

                self.pools.remove(pool)

                deleted = True

        if deleted == False:

            print(f"The pool '{pool_name}' does not exist")



    def inspect_pool(self, pool_name):

        found = False

        for pool in self.pools:

            if pool.name == pool_name:

                pool.list_agents()

                found = True

        if found == False:

            print(f"The pool '{pool_name}' does not exist.")



    def list_pools(self):

        print("\nListing Pools:\n")
        print(f"{'ID':<15}{'Pool Name':<15}{'Agent Count':<15}")
        print("="*80 + "\n")

        ctr = 1

        for pool in self.pools:

            print(f"{ctr:<15}{pool.name:<15}{len(pool.agent_list):<15}")
            ctr += 1

        print("\n" + "="*80 + "\n")


    def add_agent(self, pool_name, agent_id):

        added = False

        try:

            for pool in self.pools:

                if pool.name == pool_name:

                    agent_manager = AgentManager()

                    target_agent = agent_manager.get_agent(agent_id)

                    pool.add_agent(target_agent)

                    added = True

            if added == False:

                print(f"The pool '{pool_name}' does not exist")

        except IndexError:

            print("Invalid agent index, please type 'list agents' to check the existing agents and their indexes")


    def remove_agent(self, pool_name, agent_id):

        removed = False

        try:

            for pool in self.pools:

                if pool.name == pool_name:

                    pool.remove_agent(agent_id)

                    removed = True

            if removed == False:

                print(f"The pool '{pool_name}' does not exist")

        except IndexError:

            print("Invalid agent index inside the pool, please type 'pool list POOL_ID' to check the existing agents within a pool")


    def send_file(self, pool_name, src_path, dst_path):

        found = False

        for pool in self.pools:

            if pool.name == pool_name:

                pool.send_file(src_path, dst_path)

                found = True

        if found == False:

            print(f"The pool '{pool_name}' does not exist.")


    def execute_file(self, pool_name, command_file):

        found = False

        for pool in self.pools:

            if pool.name == pool_name:

                pool.execute_file(command_file)

                found = True

        if found == False:

            print(f"The pool '{pool_name}' does not exist.")

        

