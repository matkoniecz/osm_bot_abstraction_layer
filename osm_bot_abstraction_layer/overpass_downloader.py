import requests
import requests.exceptions
import time
from tqdm import tqdm
import random
from datetime import datetime
import lxml.etree # https://stackoverflow.com/questions/41066480/lxml-error-on-windows-attributeerror-module-lxml-has-no-attribute-etree#50529460

def sleep(time_in_s):
    for i in tqdm(range(time_in_s*10), ascii=True):
        time.sleep(0.1)

def download_overpass_query(query, filepath, timeout=1500, user_agent='overpass downloader for OSM bot (if it is overusing resources, please block it and contact matkoniecz@gmail.com)'):
    # see https://github.com/westnordost/StreetComplete/blob/6740a0b03996b929f9cf74ddb0e6afac7e3fc48e/app/src/main/res/xml/preferences.xml#L99
    faster_server ="https://lz4.overpass-api.de/api/interpreter"
    alt_server = "http://z.overpass-api.de/api/interpreter"
    server = random.choice([faster_server, alt_server])
    with open(filepath, 'w+') as file:
        file.write(get_response_from_overpass_server(server, query, timeout, user_agent))

def sleep_before_retry(error_summary, api_url):
    print("sleeping before retry due to", error_summary)
    status_url = api_url.replace("/interpreter", "/status")
    r = requests.get(status_url)
    print(r)
    print(r.text)
    sleep(100)
    print("retrying on", datetime.now().strftime("%H:%M:%S (%Y-%m-%d)"))

def get_response_from_overpass_server(api_url, query, timeout, user_agent):
    #print("sleeping before download")
    #sleep(20)
    while True:
        try:
            response = single_query_run(api_url, query, timeout, user_agent)
            # response that may be still a failure such as timeout, see https://github.com/drolbr/Overpass-API/issues/577
            # following response should be treated as a failure
            """
            <?xml version="1.0" encoding="UTF-8"?>
            <osm version="0.6" generator="Overpass API 0.7.56.9 76e5016d">
            <note>The data included in this document is from www.openstreetmap.org. The data is made available under ODbL.</note>
            <meta osm_base="2021-06-09T08:22:58Z"/>

            <remark> runtime error: Query timed out in "query" at line 4 after 2 seconds. </remark>

            </osm>
            """
            if response.status_code == 200:
                if "[out:json]" in query:
                    raise unhandled
                response_length = len(response.content.decode('utf-8'))
                print("response length:", response_length)
                # very long indicates that data was returned, some may be some massive that parsing would be outrageously expensive
                if response_length < 10_000:
                    """"
                    print("==================================================================")
                    print("================RESPONSE==========================================")
                    print(response.content.decode('utf-8'))
                    print("==================================================================")
                    print("================REMARK============================================")
                    print(parsed.find('remark'))
                    print("==================================================================")
                    print("================NOT EXISTING=======================================")
                    print(parsed.find('remarad0ddadsjjdasjadadsjdahadhadk'))
                    """
                    parsed = lxml.etree.fromstring(response.content) # yes, without .decode('utf-8')
                    if parsed.find('remark') != None:
                        raise Exception('timeout in query or other failure!' + query)


            # 429 and 503 indicate rate limiting
            # 504 appears to be a bug https://github.com/drolbr/Overpass-API/issues/220
            if response.status_code not in [429, 503, 504]:
                return response.content.decode('utf-8')
            sleep_before_retry(str(response.status_code) + " error code (response received)", api_url)
            continue
        except requests.exceptions.ConnectionError as e:
            print(e)
            sleep_before_retry("requests.exceptions.ConnectionError", api_url)
            continue
        except requests.exceptions.HTTPError as e:
            print(e.response.status_code)
            if e.response.status_code == 429 or e.response.status_code == 503:
                sleep_before_retry(e.response.status_code + " error code (HTTPError thrown)", api_url)
                continue
            raise e
        except requests.exceptions.ReadTimeout as e:
            sleep_before_retry("timeout", api_url)
            continue
    print("overpass query failed!")

def single_query_run(api_url, query, timeout, user_agent):
    print("downloading " + query)
    response = requests.post(
        api_url,
        data={'data': query},
        timeout=timeout,
        headers={'User-Agent': user_agent}
    )
    print("completed with", response.status_code, "http code")
    return response
