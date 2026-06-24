import urllib.request

url = "http://fosstorrents.com:6969/announce"

try:
    response = urllib.request.urlopen(url, timeout=10)

    print("Status:", response.status)

except Exception as e:
    print(e)