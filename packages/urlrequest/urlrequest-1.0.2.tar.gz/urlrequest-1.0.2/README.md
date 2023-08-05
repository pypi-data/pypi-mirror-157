# URL Request
## wrapper for urllib.request.urlopen


Very limited drop-in replacement for requests when you cant import requests
and need to use the built in urllib.request library 

Can be used via pip or just copy the class into your project
``` python
pip install urlrequest
```
``` python
from urlrequest import UrlRequest # as requests
```

```python
response = UrlRequest('https://httpbin.org/ip')
print(response.text)
print(response.status_code)
print(response.headers)
print(response.json)

response = UrlRequest("https://httpbin.org/basic-auth/user/password",auth=('user','password'))
print(response.text)

response = UrlRequest("https://httpbin.org/post",method="POST",json={"hello":"world"})
print(response.text)

response = UrlRequest("https://httpbin.org/image/png")
with open("test.png","wb") as f:
    f.write(response.raw)
print(response.status_code)

# drop in for requests
response = UrlRequest.get("https://httpbin.org/headers",headers={"hello":"world header test"})
print(response.text)
```