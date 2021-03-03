import requests
import requests.exceptions
import time
from tqdm import tqdm
import random

def sleep(time_in_s):
    for i in tqdm(range(time_in_s*10), ascii=True):
        time.sleep(0.1)

def download_overpass_query(query, filepath):
    # see https://github.com/westnordost/StreetComplete/blob/6740a0b03996b929f9cf74ddb0e6afac7e3fc48e/app/src/main/res/xml/preferences.xml#L99
    faster_server ="https://lz4.overpass-api.de/api/interpreter"
    alt_server = "http://z.overpass-api.de/api/interpreter"
    server = random.choice([faster_server, alt_server])
    with open(filepath, 'w+') as file:
        file.write(get_response_from_overpass_server(server, query))

def get_response_from_overpass_server(api_url, query):
    #print("sleeping before download")
    #sleep(20)
    while True:
        try:
            response = single_query_run(api_url, query)
            return response.content.decode('utf-8')
        except requests.exceptions.HTTPError as e:
            print(e.response.status_code)
            if e.response.status_code == 429 or e.response.status_code == 503:
                print("sleeping before retry due to", e.response.status_code, "error code")
                sleep(100)
                print("retrying")
                continue
            raise e
    print("overpass query failed!")

def single_query_run(api_url, query):
    print("downloading " + query)
    response = requests.post(
        api_url,
        data={'data': query},
        timeout=25000,
        headers={'User-Agent': 'overpass downloader for OSM bot'} #{"Accept-Charset": "utf-8;q=0.7,*;q=0.7"},
    )
    print("succeded with", response.status_code, "http code")
    return response
