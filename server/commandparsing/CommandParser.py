
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

import json
import os
from tabulate import tabulate
from server.listener import ListenerHandler
from server.agent import AgentManager
from server.agent import AgentHandler
from implant import ImplantGenerator
from server.pool import PoolManager
from server.pool import PoolHandler
from mtls import PKIManager

class CommandParser():

    script_dir = os.path.dirname(os.path.abspath(__file__))

    COMMAND_DEFINITIONS = os.path.join(script_dir, './command_definition.json')

    def __init__(self):

        with open(CommandParser.COMMAND_DEFINITIONS, 'r') as file:
            self.commands= json.load(file)["commands"]


    def parse_command(self, input_string):

        split_input = input_string.split()

        if not split_input:

            print("Please enter a command")

            return

        command = split_input[0]

        if len(split_input) > 1:
            subcommand = split_input[1]
        else:
            subcommand = None

        if len(split_input) > 2:
            arguments = split_input[2:]
        else:
            arguments = None

        if command in self.commands:

            command_data = self.commands[command]

            if "subcommands" in command_data:

                if subcommand != None:

                    self.parse_subcommand(command_data, subcommand, arguments)

                else:

                    print("This command requires a subcommand, please check the documentation or type 'help'")

                    return

            else:

                function_name = command_data["function"]

                try:
                    function = getattr(self, function_name)

                    function()

                except AttributeError:

                    print(f"Function {function_name} not implemented")

        else:

            print("Command not found")

            return



    def parse_subcommand(self, command_data, subcommand, arguments):

        if subcommand in command_data["subcommands"]:

            subcommand_data = command_data["subcommands"][subcommand]

            if "args" in subcommand_data:

                if arguments != None:

                    self.parse_arguments(subcommand_data, arguments)

                else:

                    print("This subcommand requires arguments, please check the documentation or type 'help'")

                    return

            else:

                function_name = subcommand_data["function"]

                try:

                    function = getattr(self, function_name)

                    function()

                except AttributeError:

                    print(f"Function {function_name} not implemented")

        else:

            print("Command not found")

            return



    def parse_arguments(self, subcommand_data, arguments):

        expected_arguments = subcommand_data["args"]

        if len(arguments) == len(expected_arguments):

            function_name = subcommand_data["function"]

            try:

                function = getattr(self, function_name)
                function(arguments)

            except AttributeError:

                print(f"Function {function_name} not implemented")

        else:

            print("The number of arguments provided does not match with the number of arguments required, please check the documentation or type 'help'")

            return


    def show_help(self):

        print("\nEyeStoneC2 - Help Pannel")
        print("-"*24)
        print("\n")

        rows = []
        for command, details in self.commands.items():

            for subcommand, info in details.get("subcommands", {}).items():

                full_command = f"{command} {subcommand}"

                args = " ".join(info.get("args", [])) if "args" in info else "NO ARGUMENTS NEEDED"

                description = info.get("description", "")

                rows.append((full_command, args, description))

        headers = ["Command", "Arguments", "Description"]

        print(tabulate(rows, headers, tablefmt="fancy_outline"))

        print("\n")



    def listener_create(self, arguments):

        local_port = arguments[0]
        listener_result = ListenerHandler.start_listener('0.0.0.0', int(local_port))

        if listener_result["status"] == "success":

            agent_info = listener_result["connection_info"]

            new_agent = AgentHandler(agent_info[0], agent_info[1])

            agent_manager = AgentManager()

            agent_manager.add_agent(new_agent)
            print(new_agent)
            new_agent.interact()

        elif listener_result["status"] == "stopped":

            print("[!] The listener was stopped and the socket was closed...")

            return

        elif listener_result["status"] == "ssl_error":

            print("[!] An SSL error happened. Please check the certificates on both server and agent")

            return

        else:
            return


    def list_agents(self):

        agent_manager = AgentManager()

        agent_manager.list_agents()

        
    def agent_interact(self, arguments):

        agent_manager = AgentManager()

        agent_id = int(arguments[0])

        agent_id -= 1

        agent_manager.interact_agent(agent_id)


    def agent_remove(self, arguments):

        agent_manager = AgentManager()

        agent_id = int(arguments[0])

        agent_id -= 1

        agent_manager.remove_agent(agent_id)


    def agent_detach(self, arguments):

        agent_manager = AgentManager()

        agent_id = int(arguments[0])

        print("\n[!] The selected agent will be uninstalled from the target machine.")
        print(f"[!] If you only want to close the connection with the agent, use the command 'agent remove {agent_id}' instead")

        confirmation = input("\n[!] Do you want to continue? (Y/N): ")

        if confirmation == "Y" or confirmation  == "y":

            agent_id -= 1

            agent_manager.detach_agent(agent_id)


    def implant_create(self, arguments):

        localhost = arguments[0]
        localport = arguments[1]
        platform = arguments[2]

        generator = ImplantGenerator()

        generator.generate(localhost, localport, platform)


    def pool_create(self, arguments):

        print("\n[+] Creating pool...")

        pool_name =  arguments[0]

        new_pool = PoolHandler(pool_name)

        pool_manager = PoolManager()

        pool_manager.add_pool(new_pool)

        print(f"\n[+] Pool '{pool_name}' created successfully!")


    def pool_add_agent(self, arguments):

        pool_name = arguments[0]

        agent_id = int(arguments[1]) - 1

        pool_manager = PoolManager()

        pool_manager.add_agent(pool_name, agent_id)


    def pool_remove_agent(self, arguments):

        pool_name = arguments[0]

        agent_id = int(arguments[1]) - 1

        pool_manager = PoolManager()

        pool_manager.remove_agent(pool_name, agent_id)


    def pool_inspect(self, arguments):

        pool_name = arguments[0]

        pool_manager = PoolManager()

        pool_manager.inspect_pool(pool_name)


    def list_pools(self):

        pool_manager = PoolManager()

        pool_manager.list_pools()


    def pool_delete(self, arguments):

        pool_manager =  PoolManager()

        pool_name = arguments[0]

        print(f"\n[!] The pool '{pool_name}' will be deleted. This action will not delete the agents inside the pool")

        confirmation = input("[!] Do you want to continue? (Y/N): ")

        if confirmation == "Y" or confirmation == "y":

            pool_manager.delete_pool(pool_name)


    def agent_sendfile(self, arguments):

        agent_id = int(arguments[0]) - 1

        src_path = arguments[1]

        if os.path.isfile(src_path) == False:

            print(f"The file '{src_path}' does not exist.")

        else:

            dst_path = arguments[2]

            agent_manager = AgentManager()

            agent_manager.send_file(agent_id, src_path, dst_path)


    def pool_sendfile(self, arguments):

        pool_name = arguments[0]

        src_path = arguments[1]

        if os.path.isfile(src_path) == False:

            print(f"The file '{src_path}' does not exist.")

        else:

            dst_path = arguments[2]

            pool_manager = PoolManager()

            pool_manager.send_file(pool_name, src_path, dst_path)


    def pool_execute(self, arguments):

        pool_name = arguments[0]

        command_file = arguments[1]

        if os.path.isfile(command_file) == False:

            print(f"The command file '{command_file}' does not exist.")

        else:

            pool_manager = PoolManager()

            pool_manager.execute_file(pool_name, command_file)


    def generate_ca(self):

        confirmation = input("[!] Any existing Certificate Authority will be deleted. Do you want to continue? (Y/N): ")

        if confirmation == "Y" or confirmation == "y":

            PKIManager.generate_ca()


    def generate_server(self):

        confirmation = input("[!] Any existing server certificate will be deleted. Do you want to continue? (Y/N): ")

        if confirmation == "Y" or confirmation == "y":

            PKIManager.generate_server()




        




