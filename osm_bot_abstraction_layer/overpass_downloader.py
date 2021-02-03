import urllib.request, urllib.error, urllib.parse
import time
from tqdm import tqdm
import random

def sleep(time_in_s):
    for i in tqdm(range(time_in_s*10), ascii=True):
        time.sleep(0.1)

def download_overpass_query(query, filepath):
    query = urllib.parse.quote(query)
    # see https://github.com/westnordost/StreetComplete/blob/6740a0b03996b929f9cf74ddb0e6afac7e3fc48e/app/src/main/res/xml/preferences.xml#L99
    faster_server ="https://lz4.overpass-api.de/api/interpreter"
    alt_server = "http://z.overpass-api.de/api/interpreter"
    server = random.choice([faster_server, alt_server])
    url = server +"?data=" + query
    with open(filepath, 'w+') as file:
        file.write(overpass_download(url))

def overpass_download(url):
    print("sleeping before download")
    sleep(20)
    while True:
        try:
            print("downloading " + url)
            request = urllib.request.Request(url,headers={'User-Agent': 'overpass downloader for OSM bot'})
            response = urllib.request.urlopen(request, timeout=25000)
            print("succeded with", response.getcode(), "http code")
            return response.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            print(e.getcode())
            if e.getcode() == 429 or e.getcode() == 503:
                print("sleeping before retry due to", e.getcode(), "error code")
                sleep(100)
                print("retrying")
                continue
            raise e
        except urllib.error.URLError as e:
            print(("URLError for url " + url))
            print(e)
            return
    print("overpass query failed!")
