
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

from OpenSSL import crypto
import os
import secrets

class PKIManager():

    ca_dir = './mtls/certificate_authority'
    server_dir = './mtls/server'
    agents_dir = './mtls/agents'
    

    @staticmethod
    def generate_ca():
        
        os.makedirs(PKIManager.ca_dir, exist_ok=True)

        print("\n[...] Starting self-signed Certificate Authority generation...\n")

        print("\t[...] Generating key pair...")
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)

        print("\t[...] Generating and signing CA certificate...")
        cert = crypto.X509()
        cert.get_subject().CN = "EyeStoneCA"
        cert.set_serial_number(PKIManager.generate_serial_number())
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)

        cert.add_extensions([crypto.X509Extension(b"basicConstraints", True, b"CA:TRUE"),
                             crypto.X509Extension(b"keyUsage", True, b"keyCertSign"),
                             crypto.X509Extension(b"subjectKeyIdentifier", False, b"hash", subject=cert)
                             ])

        cert.sign(key, 'sha256')

        print("\t[...] Dumping private key and certificate...")

        with open(f"{PKIManager.ca_dir}/ca.key", "wb") as key_file:
            key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

        with open(f"{PKIManager.ca_dir}/ca.crt", "wb") as cert_file:
            cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

        print("\n[+] Done!")


    @staticmethod
    def generate_server():

        os.makedirs(PKIManager.server_dir, exist_ok=True)

        print("\n[...] Starting server certificate generation...")

        print("\t[...] Generating server key pair...")

        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)

        print("\t[...] Dumping server private key...")
        
        with open(f"{PKIManager.server_dir}/server.key", "wb") as key_file:
            key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

        print("\t[...] Generating CSR for the server certificate...")

        req = crypto.X509Req()
        subject = req.get_subject()
        subject.CN = f"EyeStoneServer"
        req.set_pubkey(key)
        req.sign(key, "sha256")

        print("\t[...] Dumping CSR...")

        with open(f"{PKIManager.server_dir}/server.csr", "wb") as cert_file:
            cert_file.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, req))

        print("\t[...] Signing the CSR with the EyeStoneC2 Certificate Authority...")

        PKIManager.sign_csr(req, f"{PKIManager.server_dir}/server.crt")

        print("\n[+] Done!")


    @staticmethod
    def generate_agent(agent_name):
    
        agent_dir = os.path.join(PKIManager.agents_dir, agent_name)
        os.makedirs(agent_dir, exist_ok=True)

        print("\n[...] Starting agent certificate generation...")

        print(f"\n[...] Agent name ---> {agent_name}")

        print("\t[...] Generating agent key pair...")

        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)

        print("\t[...] Dumping agent private key...")
    
        with open(f"{agent_dir}/agent.key", "wb") as key_file:
            key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

        print("\t[...] Generating CSR for the agent certificate...")

        req = crypto.X509Req()
        subject = req.get_subject()
        subject.CN = f"EyeStoneAgent_{agent_name}"
        req.set_pubkey(key)
        req.sign(key, "sha256")

        print("\t[...] Dumping CSR...")

        with open(f"{agent_dir}/agent.csr", "wb") as cert_file:
            cert_file.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, req))

        print("\t[...] Signing the CSR with the EyeStoneC2 Certificate Authority...")

        PKIManager.sign_csr(req, f"{agent_dir}/agent.crt")

        print("\n[+] Done!")


    @staticmethod
    def sign_csr(req, cert_out_path):

        print("\t[...] Loading the CA private key and certificate...")

        try:

            with open(f"{PKIManager.ca_dir}/ca.key", "rb") as key_file:
                ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, key_file.read())

            with open(f"{PKIManager.ca_dir}/ca.crt", "rb") as ca_cert_file:
                ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, ca_cert_file.read())

            print("\t[...] Creating certificate based on server CSR...")

            cert = crypto.X509()
            cert.set_subject(req.get_subject())
            cert.set_serial_number(PKIManager.generate_serial_number())
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)
            cert.set_issuer(ca_cert.get_subject())
            cert.set_pubkey(req.get_pubkey())
            cert.sign(ca_key, "sha256")

            print("\t[...] Dumping certificate...")

            with open(cert_out_path, "wb") as cert_file:
                cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

        except FileNotFoundError:

            print("\n[!] Error while signign the certificate. Make sure the CA private key and certificate are available inside the 'mtls/certificate_authority' directory")
            print("\n[!] If you have not generated the CA yet, generate it using the following command: mtls cert-auth")


    @staticmethod
    def generate_serial_number():

        serial_number = secrets.randbits(64)

        return serial_number

    


