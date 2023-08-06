import urllib.request
import http.cookiejar
import json

# for test only

filename = "cookie.txt"
cookie = http.cookiejar.MozillaCookieJar(filename)
# for item in cookie:
#     print(item.name, item.value)
handler = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(handler)
loginVO = {
    "usernameORemail": "thunlp",
    "passWord": "thunlp",
}
req = urllib.request.Request("http://8.130.179.17:8080/bmb/api/v1/account/login",
                             headers={"Content-Type": "application/json"},
                             data=json.dumps(loginVO).encode("utf-8"),
                             method="POST")
response = opener.open(req)
cookie.save(ignore_discard=True, ignore_expires=True)  # 保存cookie到文件
# for item in cookie:
#     print(item.name, item.value)
