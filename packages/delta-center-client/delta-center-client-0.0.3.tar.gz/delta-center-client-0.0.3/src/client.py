# -*- coding: utf-8 -*-

import json
from numpy import full
import oss2
from getpass import getpass
import sys
import logging
from urllib import request
from .utils import checkValueSanity, getConfigFromFile, getToken, loadCookie, makeReq
from urllib.parse import urlencode
import os
import pathlib
from zipfile import ZipFile
import yaml
import os

logger = logging.getLogger("DeltaCenter-Client")
logger.setLevel(logging.INFO)


class Client:
    def __init__(self, config) -> None:
        self.server = config.server
        self.api_prefix = f"{config.server}/delta/api/v1"
        self.preview_prefix = f"{config.server}/delta/template?id="
        self.debug = config.debug
        self.required_params = config.delta.requiredParams
        self.sso_login_url = config.sso.login
        self.sso_checkToken_url = config.sso.checkToken
        self.filesInZip = config.delta.filesInZip
        self.logined = False
        self.loginVO = None
        self.entiy_type = "delta"
        self.action = ""
        self.keymap = {  # key maps for properties present in database
            "name": "name",
            "dataset": "dataset",
            "backbone_model": "model",
            "delta_type": "type",
            "train_tasks": "task"
        }

    def percentage(self, consumed_bytes, total_bytes):
        if total_bytes:
            rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
            print(f'\r{rate}% {self.action} {self.current_file} ', end='')
            sys.stdout.flush()

    def getParams(self, path) -> dict:
        # get params from file, ask for user input if not present
        if os.path.exists(path):
            params = getConfigFromFile(path)
        else:
            params = dict()
        return params

    def getHeaders(self):
        return {
            'Content-Type': 'application/json',
        }

    def isExistByName(self, full_name: str) -> bool:
        query_str = urlencode({"name": full_name})
        url = f"{self.api_prefix}/delta/exists?{query_str}"
        req = request.Request(url, headers=self.getHeaders(), method="GET")
        response = makeReq(req)
        return response["data"]

    def login(self, force_relogin=False):
        if not force_relogin:
            token = getToken()
            req = request.Request(self.sso_checkToken_url+f"?token={token}", headers=self.getHeaders(), method="POST")
            response = makeReq(req)
            if response["code"] == 0:
                self.user = response["data"]["username"]
                self.logined = True
        while not self.logined:
            if 'DELTACENTERUSERNAME' in os.environ:
                self.user = user =  os.environ['DELTACENTERUSERNAME']
            else:
                self.user = user = input("username:")
            if 'DELTACENTERPASSWORD' in os.environ:
                passwd = os.environ['DELTACENTERPASSWORD']
            else:
                passwd = getpass("password:")
            loginVO = {
                "usernameORemail": user,
                "passWord": passwd,
            }
            # if self.debug:
            #     self.logined = True
            #     self.token = user
            #     break
            # login request
            loginVO = json.dumps(loginVO).encode("utf-8")
            req = request.Request(self.sso_login_url, data=loginVO,
                                  headers=self.getHeaders(), method="POST")
            response = makeReq(req, save_cookie=True)
            code, data, message = response["code"], response["data"], response["message"]
            if code == 0:
                self.logined = True
            else:
                print(message)
        return self.logined

    def fileTransferReq(self, params: dict={}, action="upload", method="POST", jsondata=None):
        query_str = urlencode(params)
        url = f"{self.api_prefix}/file/{action}?{query_str}"
        req = request.Request(url, data=json.dumps(jsondata).encode(
            "utf-8"), headers=self.getHeaders(), method=method)
        return req

    def getDownloadUrl(self, req):
        # locally assemble url, WILL NOT contribute to downloads count
        return f"https://openprompt.oss-cn-beijing.aliyuncs.com/{req.user}/{req.deltaName}"

    def findReadmeFile(self, files) -> str:
        for f in files:
            if f.lower().startswith("readme"):
                return f
        return ""

    def getFilesFromPath(self, path, zipped_file):
        # recursively get file from path, with no prefix
        # both files and fileTransferDTO is relative to path
        cwd = os.getcwd()
        os.chdir(path)
        # package necessary files into payload.zip
        # zipped_file = "payload.zip"
        zipObj = ZipFile(zipped_file, 'w')
        for f in self.filesInZip:
            if os.path.exists(f):
                zipObj.write(f)
            else:
                logger.warning(f"Missing required file: {f}")
                exit(0)
        zipObj.close()
        files = []
        for dir, curdir, fs in os.walk('.'):
            for f in fs:
                name = os.path.normpath(os.path.join(dir, f))
                if name in self.filesInZip: # skip zipped files
                    continue
                if name.startswith('.'):  # skip hidden files
                    continue
                files.append(name)
        assert zipped_file in files
        # switch zipped file to first
        index = files.index(zipped_file)
        if index > 0:
            files[0], files[index] = files[index], files[0]
        logger.debug(files)
        fileTransferDTO = [{
            "name": name,
            "size": os.path.getsize(name)
        } for name in files]
        os.chdir(cwd)
        return files, fileTransferDTO

    def upload(self, base_dir: str, params_override: dict = dict(), force_overwrite: bool = False, filesInZip: list = None):
        if filesInZip is not None:
            self.filesInZip = filesInZip

        raw_params = self.getParams(os.path.join(base_dir, "config.yml"))
        raw_params.update(params_override)

        logger.info("Parameters to upload:\n{}".format(raw_params))
        extension = {}
        params = {}

        for key, val in raw_params.items():
            database_key = self.keymap.get(key)
            if database_key is None:
                extension[key] = val
            else:
                params[database_key] = val
        params["extension"] = json.dumps(extension)
        for key in self.required_params:
            if params.get(key) is None:
                params[key] = input(
                    f"Please enter {key} of {self.entiy_type}:")
        # deltaName should not conatin "=" or "/"
        short_name = params["name"]
        while not checkValueSanity("name", short_name, forbid_char=["=", "/"], min_len=1, max_len=128):
            short_name = input(
                f"Please enter a valid name for {self.entiy_type}:")
        # login and set self.user
        if not self.login():
            exit(0)
        # used for official delta templates
        if params.get("_no_prefix"):
            delta_name = short_name
            params.pop("_no_prefix")
        else:
            delta_name = f"{self.user}/{short_name}"

        # zip files and prepare files to upload
        zip_file = f"{short_name}.zip"
        files, fileTransferDTO = self.getFilesFromPath(base_dir, zipped_file=zip_file)
        assert len(files) > 0

        params["name"] = delta_name
        params["readme_res"] = self.findReadmeFile(files)
        # check if delta exists
        if not force_overwrite and self.isExistByName(delta_name):
            if input(f"{delta_name} already exists. Do you want to overwrite it? (Y/n)").lower() != "y":
                exit(0)
        # get upload urls
        req = self.fileTransferReq(jsondata={"files": fileTransferDTO, "deltaInfoVO": params})
        response = makeReq(req)
        if response["code"] != 0:
            print(response["message"])
            exit(0)
        urls = response["data"]
        logger.debug(urls)
        if urls is None or len(urls) == 0:
            print("Server Internal Error (returned empty urls)")
            exit(0)
        bucket = oss2.Bucket(
            auth=None, endpoint="pseudoendpoint", bucket_name="pseudobucket")
        response = None
        for i, url in enumerate(urls):
            self.current_file = files[i]
            logger.debug(url)
            result = bucket.put_object_with_url_from_file(url, os.path.join(
                base_dir, files[i]), headers=None, progress_callback=self.percentage)
            print()
            if i == 0:
                response = eval(result.resp.read().decode('utf-8'))
        # remove payload.zip
        os.remove(os.path.join(base_dir, zip_file))
        if response:
            deltaId = response["message"]
            print(f"Upload success! See {self.preview_prefix}{deltaId} for detail.")
        else:
            print("Upload failed. Please check the tutorial for help.")

    def download(self, full_name: str, dest: str = None, clean=True, force_download=False):
        if dest is None:
            dest = full_name
        req = self.fileTransferReq(
            {"name": full_name}, action="download", method="GET")
        # url = self.get_download_url(req)
        response = makeReq(req)
        url = response["data"]
        if len(url) == 0:
            print(f"Cannot get valid url. Please check the name of delta.")
            exit(0)
        pathlib.Path(dest).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Downloading {url}")
        bucket = oss2.Bucket(
            auth=None, endpoint="pseudoendpoint", bucket_name="pseudobucket")
        self.action = "Download"
        short_name = full_name.split("/")[-1]
        self.current_file = f"{short_name}.zip"
        path = os.path.join(dest, self.current_file)
        path_unzip = os.path.join(dest, short_name)
        if os.path.exists(path) and not force_download:
            logger.warning("Reuse the cached checkpoint in {}".format(path))
        elif os.path.exists(path_unzip) and not force_download:
            logger.warning("Reuse the cached checkpoint in {}".format(path_unzip))
        else:
            result = bucket.get_object_with_url_to_file(
                url, path, progress_callback=self.percentage)
            print()
            logger.debug(result.status)
            logger.info("Downloaded to {}".format(path_unzip))
        if not os.path.exists(path_unzip) or force_download:
            with ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(path_unzip)
        if clean and os.path.exists(path):
            os.remove(path)
        return path_unzip

    def create_yml(self, save_dir, config):
        f = open("{}/config.yml".format(save_dir), 'w')
        yaml.safe_dump(vars(config), f)
        f.close()

def help():
    print("""Usage:
        Upload/Download: python -m DeltaCenter [upload/download] [delta directory]
        Login: python -m DeltaCenter login
        """
    )


if __name__ == "__main__":
    cfg = getConfigFromFile("config.yml")
    client = Client(cfg)
    logger_level = logger.DEBUG if cfg.debug else logger.DEBUG
    logger.basicConfig(filename=None, level=logger_level,
                        format="[%(levelname)s] %(message)s")
    if len(sys.argv) < 3:
        help()
        exit(1)
    action = sys.argv[1]
    if action.lower() in ["up", "upload"]:
        path = sys.argv[2]
        client.upload(base_dir=path)
    elif action.lower() in ["down", "download"]:
        oss_path = sys.argv[2]
        client.download(oss_path)
