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

import json
import os
import sys
import socket
import signal
from dotenv import load_dotenv

load_dotenv()

from server.agent import AgentHandler
from server.commandparsing import CommandParser
from server.agent import AgentManager

def ascii_art():

    return '''

░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░░▒▓███████▓▒░▒▓████████▓▒░▒▓██████▓▒░░▒▓███████▓▒░░▒▓████████▓▒░       ░▒▓██████▓▒░░▒▓███████▓▒░  
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░         ░▒▓█▓▒░  ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░         ░▒▓█▓▒░  ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             ░▒▓█▓▒░             ░▒▓█▓▒░ 
░▒▓██████▓▒░  ░▒▓██████▓▒░░▒▓██████▓▒░  ░▒▓██████▓▒░   ░▒▓█▓▒░  ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░        ░▒▓█▓▒░       ░▒▓██████▓▒░  
░▒▓█▓▒░         ░▒▓█▓▒░   ░▒▓█▓▒░             ░▒▓█▓▒░  ░▒▓█▓▒░  ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             ░▒▓█▓▒░      ░▒▓█▓▒░        
░▒▓█▓▒░         ░▒▓█▓▒░   ░▒▓█▓▒░             ░▒▓█▓▒░  ░▒▓█▓▒░  ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░        
░▒▓████████▓▒░  ░▒▓█▓▒░   ░▒▓████████▓▒░▒▓███████▓▒░   ░▒▓█▓▒░   ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░       ░▒▓██████▓▒░░▒▓████████▓▒░ 


                                                        Red Teaming Framework

                                        By Gabriel Pérez Navarro (https://github.com/gperez01)                                                                                                                                     

'''

def sig_handler(sig, frame):

    print("[!] Ctrl + C")
    shut_down()
    sys.exit(1)


def shut_down():

    print("Closing communication with all agents...")

    agent_manager = AgentManager()
    agent_manager.remove_all_agents()

    print("Communication with all agents is now closed, exiting...")


def clear_screen():

    os.system('clear')


def parse_command(input_string, command_parser):

    if input_string == 'exit':

        shut_down()
        sys.exit(0)

    elif input_string == 'help':

        command_parser.show_help()

    elif input_string  == 'clear':
        
        clear_screen()

    else:

        command_parser.parse_command(input_string)

def wait_input():

    prompt = ">>"

    command_parser = CommandParser()

    while True:

        input_string = input(f"{prompt} ")

        parse_command(input_string, command_parser)


def init_c2():

    print(ascii_art())

    agent_manager = AgentManager()  # Unique AgentManager() instance (singleton)

    print("Type 'help' to print the help pannel\n")

    wait_input()


if __name__ == "__main__":

    signal.signal(signal.SIGINT, sig_handler)

    init_c2()
