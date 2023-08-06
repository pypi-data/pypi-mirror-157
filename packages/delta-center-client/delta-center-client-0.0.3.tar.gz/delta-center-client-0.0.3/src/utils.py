from yacs.config import CfgNode
import os
import http.cookiejar
import json
import urllib.request
import sys
import logging


def getConfigFromFile(path):
    cfg = CfgNode(new_allowed=True)
    cfg.merge_from_file(path)
    return cfg


def saveCookie(cookie, path='login.cookie'):
    path = os.path.join(os.path.dirname(__file__), path)
    cookie.save(path, ignore_discard=True, ignore_expires=False)
    # with open(os.path.join(os.path.dirname(__file__), path), 'wb') as f:
    #     pickle.dump(cookie, f)


def loadCookie(path='login.cookie'):
    path = os.path.join(os.path.dirname(__file__), path)
    cookie = http.cookiejar.MozillaCookieJar()
    try:
        if os.path.exists(path):
            cookie.load(path, ignore_discard=True, ignore_expires=False)
    except http.cookiejar.LoadError as ex:
        logging.info(ex)
        pass
    # if os.path.exists(path):
    #     with open(path, 'rb') as f:
    #         cookie = pickle.load(f)
    return cookie

def getToken():
    cookie = loadCookie("login.cookie")
    token = ""
    for item in cookie:
        if item.name == "JWT-TOKEN":
            token = item.value
            break
    return token

def makeReq(req: urllib.request.Request, save_cookie=False):
    cookie = loadCookie(path='login.cookie')
    try:
        # 利用urllib2库的HTTPCookieProcessor对象来创建cookie处理器
        handler = urllib.request.HTTPCookieProcessor(cookie)
        opener = urllib.request.build_opener(handler)  # 通过handler来构建opener
        r = opener.open(req)  # 此处的open方法同urllib2的urlopen方法，也可以传入request
        # r = request.urlopen(req)
        if save_cookie:
            saveCookie(cookie, path='login.cookie')
    except Exception as ex:
        raise
    return json.loads(r.read().decode('utf-8'))


def checkValueSanity(key, value, forbid_char=[], must_char=[], min_len=-1, max_len=4294967296) -> bool:
    msg = []
    bad_ents = []
    for c in forbid_char:
        if c in value:
            bad_ents.append(c)
    ents = " or ".join(bad_ents)
    if len(bad_ents) > 0:
        msg.append(f"should not contain {ents}")
    miss_ents = []
    for c in must_char:
        if c not in value:
            miss_ents.append(c)
    ents = " and ".join(miss_ents)
    if len(ents) > 0:
        msg.append(f"must contain {ents}")
    if len(value) > max_len or len(value) < min_len:
        msg.append(f"should have length between {min_len} and {max_len}")
    if len(msg) > 0:
        print(f"{key} does not meet the following requirements:")
        for m in msg:
            print(f"  ·{m}")
        return False
    else:
        return True
