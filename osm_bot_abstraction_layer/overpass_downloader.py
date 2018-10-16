import urllib.request, urllib.error, urllib.parse
import time

def download_overpass_query(query, filepath):
    query = urllib.parse.quote(query)
    url = "http://overpass-api.de/api/interpreter?data=" + query
    with open(filepath, 'w+') as file:
        file.write(overpass_download(url))

def overpass_download(url):
    while True:
        try:
            print("downloading " + url)
            resource = urllib.request.urlopen(url)
            return resource.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            print(e.getcode())
            if e.getcode() == 429 or e.getcode() == 503:
                time.sleep(60)
                continue
            raise e
        except urllib.error.URLError as e:
            print(("URLError for url " + url))
            print(e)
            return
