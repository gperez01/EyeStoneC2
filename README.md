
# EyeStoneC2

<p align="center">
  <img src="https://github.com/gperez01/EyeStoneC2/blob/405eef4a24a65a14f867e60d4caa1514556e30f0/images/logo.png" alt="eyestonec2" width="500" height="500"/>
</p>

EyeStoneC2 is an open-source, modular and customizable Red Teaming framework designed to provide companies a usable, operable and maintainable offensive security solution.

It is composed of a main C2 server and two independent compilation servers, responsible for compiling malware implants.

EyeStoneC2 supports C2 over mTLS by default.

[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)

# v1.0.0-rc.1 / `main`

**IMPORTANT**: this is the release candidate for the version 1.0.0. This version, although being almost complete, **is not meant to be deployed on production environments**.
## Main features

- External compilation servers
- Agent communication via mTLS
- Dynamic agent and pool management
- Beaconing signal transmission from agent to server for network stealth
- Asynchronous command execution and file transmission to agents within the same pool
- System enumeration via syscalls and Win32 API


## Installation

The C2 main server installation is as easy as follows:

```bash
  git clone https://github.com/gperez01/EyeStoneC2.git
  cd EyeStoneC2
  pip install -r requirements.txt
```
This is the EyeStoneC2 architecture's physical view:

![image_alt](https://github.com/gperez01/EyeStoneC2/blob/b7bbef5c48ecfb011c50b2d23e8113f4f4304f5f/images/physical_view.png)

The EyeStoneC2 needs two **external compilation servers** (Windows and Linux) to pack python malware implants into a standalone executable.

These compilation servers have been tested with the following operating systems:

- **Windows Server 2022 Datacenter Core**
- **Ubuntu Server 24.04 LTS**

Both compilation servers need Python3 with the following dependencies:

- FastAPI
- PyDantic
- PyInstaller
- Uvicorn

```python
pip install fastapi pydantic pyinstaller uvicorn
```
The following directories must be created on each compilation server:

**Linux**:
```
/opt/webserver
/opt/workspace/command_and_control
/opt/workspace/implants/linux/implants
/opt/workspace/implants/linux/workfolder
```
**Windows**:
```
C:\webserver
C:\workspace\command_and_control
C:\workspace\implants\windows\implants
C:\workspace\implants\windows\workfolder
```
After directory creation, the following files must be placed inside the compilation servers:

| **Source (repository)**  | **Destination (Windows comp. server)** |
| ------------- | ------------- |
| compilation_server/windows/webserver_main.py  | C:\webserver\webserver_main.py  |
| implant/windows_template.py | C:\workspace\command_and_control\windows_template.py |

| **Source (repository)** | **Destination (Linux comp. server)**
| ------------- | ------------- |
| compilation_server/linux/webserver_main.py  | /opt/webserver/webserver_main.py  |
| implant/linux_template.py | C:\workspace\command_and_control\linux_template.py |


After placing the files inside the compilation servers, the HTTP server can be deployed (run inside "C:\webserver" or "/opt/webserver" directory)
```bash
uvicorn webserver_main:app –-host 0.0.0.0 –-port 8080 --reload
```

## Configuration and Usage
Inside the .env file, both compilation servers IPv4 and port must be specified:
```bash
COMPILATION_SERVER_WINDOWS=<IP_ADDR>:<PORT>
COMPILATION_SERVER_LINUX=<IP_ADDR>:<PORT>
```
Deploy the C2 server:
```
python3 main.py 
```
Generate EyeStoneC2 Certificate Authority:
```
>> mtls cert-auth
```
Generate EyeStoneC2 server certificate:
```
>> mtls server
```
Show full help:
```
>> help
```

# License
This software is licensed under the **Affero General Public License v3.0 (AGPLv3.0)**. Please refer to the `LICENSE` file for more details.

By using this tool, **you agree to these terms in full.**

# Legal Disclaimer
EyeStoneC2 is an offensive security framework. Some of its components could be flagged as malware by security solutions. **The use of this software in environments where explicit authorization has not been provided is extrictly prohibited.** It is solely the user's responsibility to ensure lawful and ethical use of EyeStoneC2.

## TODO
- Command definition documentation
- CommandParser data type verification
