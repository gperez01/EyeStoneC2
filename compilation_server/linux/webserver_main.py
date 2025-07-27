
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

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess
from datetime import datetime 
import re
import os


app = FastAPI()

class Implant(BaseModel):

    localhost: str
    localport: int 
    filename: str


@app.get("/")
def root():
    return {"message": "Hello World!"}


@app.post("/compile")
def compile_request(implant: Implant):

    localhost = implant.localhost
    localport = implant.localport
    filename = implant.filename

    modify_template(filename, localhost, localport)

    comp_ret = compile_implant(localhost, localport, filename)

    if comp_ret == 0:
        filepath = get_file_path(filename)
        return FileResponse(path=filepath, filename=f'{filename}', media_type='application/octet-stream')

    else:
        return {"compilation status": "failed"}


def modify_template(filename, localhost, localport):

    with open('/opt/workspace/command_and_control/linux_template.py', 'r') as srcfile:

        content = srcfile.read()

        with open(f'/opt/workspace/command_and_control/{filename}.py', 'w') as dstfile:

            new_content = re.sub('IP_PLACEHOLDER', localhost, content)
            new_content = re.sub('PORT_PLACEHOLDER', str(localport), new_content)

            dstfile.write(new_content)


def compile_implant(localhost, localport, filename):

    print(f"[INFO] {datetime.now()} - Compilation started - LHOST={localhost}; LPORT={localport}; FILENAME={filename}")

    compilation = subprocess.run(['pyinstaller', '--onefile', '--distpath', '/opt/workspace/implants/linux/implants', '--workpath', '/opt/workspace/implants/linux/workfolder', '--specpath', '/opt/workspace/implants/linux/workfolder', '--name', filename, f'/opt/workspace/command_and_control/{filename}.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if compilation.returncode != 0:

        print (f"[ERROR] {datetime.now()} - Compilation failed - LHOST={localhost}; LPORT={localport}; FILENAME={filename}")

    else:

        print (f"[INFO] {datetime.now()} - Compilation succeeded - LHOST={localhost}; LPORT{localport}; FILENAME={filename}")

    delete_custom_template(filename)
    return compilation.returncode


def get_file_path(filename):

    return f'/opt/workspace/implants/linux/implants/{filename}'


def delete_custom_template(filename):

    if os.path.exists(f"/opt/workspace/command_and_control/{filename}.py"):

        os.remove(f"/opt/workspace/command_and_control/{filename}.py")



    

    

    
