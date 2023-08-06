from pkg_resources import Requirement, resource_filename
from .utils import getConfigFromFile
from .client import Client, help
import os, sys
import logging

cfg_path = os.path.join(os.path.dirname(__file__), 'config.yml')
cfg = getConfigFromFile(cfg_path)
OssClient = Client(cfg)