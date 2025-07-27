
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
import signal
import ssl

class ListenerHandler():

    @staticmethod
    def start_listener(host, port):

        print(f"\n[...] Starting listener: {host}:{port}")

        try:
            
            server_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            server_context.verify_mode = ssl.CERT_REQUIRED
            
            server_context.load_cert_chain(certfile='./mtls/server/server.crt', keyfile='./mtls/server/server.key')
            server_context.load_verify_locations(cafile='./mtls/certificate_authority/ca.crt')

            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((host, port))
            server_socket.listen()

            def sig_handler(sig, frame):
                print("\n[!] Ctrl + C - Listener stopped by user")
                raise InterruptedError()

            signal.signal(signal.SIGINT, sig_handler)

            agent_socket, agent_addr = server_socket.accept()

            agent_socket_mtls = server_context.wrap_socket(agent_socket, server_side=True)

            print(f"[!] New TCP connection received from {agent_addr[0]}:{agent_addr[1]}")

            return {"status": "success", "connection_info": [agent_socket_mtls, agent_addr]}

        except InterruptedError:

            print(f"\n[!] Closing the following socket: {host}:{port}\n")

            server_socket.close()

            return {"status": "stopped"}

        except ssl.SSLError as e:

            print(f"\n[!] Error during the mTLS negotiation. Please check the involved certificates and try again...")

            server_socket.close()

            agent_socket.close()

            return {"status": "ssl_error"}


