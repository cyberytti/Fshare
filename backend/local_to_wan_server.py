import os

def run_wan_server():
    os.system("ssh -p 443 -R0:localhost:8000 a.pinggy.io -o StrictHostKeyChecking=no -T")