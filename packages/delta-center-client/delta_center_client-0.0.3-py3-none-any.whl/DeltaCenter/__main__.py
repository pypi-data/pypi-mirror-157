from pkg_resources import Requirement, resource_filename
from .utils import getConfigFromFile
from .client import Client, help
import os, sys
import logging

cfg_path = os.path.join(os.path.dirname(__file__), 'config.yml')
cfg = getConfigFromFile(cfg_path)
client = Client(cfg)
logging.basicConfig(filename=None, level=logging.INFO, format="[%(levelname)s] %(message)s")
def require_args(cnt):
    if len(sys.argv) < cnt+1:
        help()
        exit(1)
require_args(1)
action = sys.argv[1]
if action.lower() in ["up", "upload"]:
    require_args(2)
    path = sys.argv[2]
    client.upload(base_dir=path)
elif action.lower() in ["down", "download"]:
    require_args(2)
    oss_path = sys.argv[2]
    client.download(oss_path)
elif action.lower() == "login":
    if client.login(force_relogin=True):
        print("Log in Successful! Now you can upload without log in.")
