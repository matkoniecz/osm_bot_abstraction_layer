import requests
import requests.exceptions
import time
from tqdm import tqdm
import random
from datetime import datetime
import lxml.etree # https://stackoverflow.com/questions/41066480/lxml-error-on-windows-attributeerror-module-lxml-has-no-attribute-etree#50529460
import urllib3

def sleep(time_in_s):
    for i in tqdm(range(time_in_s*10), ascii=True):
        time.sleep(0.1)

def download_overpass_query(query, filepath, timeout=None, user_agent='overpass downloader for OSM bot (if it is overusing resources, please block it and contact matkoniecz@gmail.com)'):
    with open(filepath, 'w+') as file:
        file.write(get_response_from_overpass_server(query, timeout, user_agent))

def sleep_before_retry(error_summary, api_url):
    print("sleeping before retry due to", error_summary)
    print()
    print("info from /status endpoint about our quota:")
    status_url = api_url.replace("/interpreter", "/status")
    r = requests.get(status_url)
    print(r.text)
    sleep(100)
    print()
    print("retrying on", datetime.now().strftime("%H:%M:%S (%Y-%m-%d)"))

def show_retry_number(retry_count):
    if retry_count>0:
        print("retry number " + str(retry_count))
    else:
        print("the first attempt")

def get_response_from_overpass_server(query, timeout, user_agent):
    #print("sleeping before download")
    #sleep(20)
    time_of_query_start = None
    retry_count = 0
    while True:
        try:
            # see https://github.com/westnordost/StreetComplete/blob/6740a0b03996b929f9cf74ddb0e6afac7e3fc48e/app/src/main/res/xml/preferences.xml#L99
            faster_server ="https://lz4.overpass-api.de/api/interpreter"
            alt_server = "http://z.overpass-api.de/api/interpreter"
            french_server = "https://overpass.openstreetmap.fr/api/interpreter" # dead as of 2022-02-17
            api_url = random.choice([faster_server, alt_server])
            print("using", api_url)
            if "is_closed" in query:
                if api_url == french_server:
                    print("skipping as french server is not supporting is_closed (as of 2021-07-20) - new server will be randomised - note that this check is dumb and will skip also when it is in comment/tag/etc. see https://github.com/osm-fr/infrastructure/issues/323 ")
                    continue
            if "nwr(" in query or "nwr[" in query:
                if api_url == french_server:
                    print("skipping as french server is not supporting nwr shortcut (as of 2021-08-27) - new server will be randomised - note that this check is dumb and will skip also when it is in comment/tag/etc, see https://github.com/osm-fr/infrastructure/issues/323")
                    continue

            time_of_query_start = time.time()
            if retry_count>0:
                response = single_query_run(api_url, query, timeout, user_agent, "retry number " + str(retry_count))
            else:
                response = single_query_run(api_url, query, timeout, user_agent, "the first attempt")
            show_retry_number(retry_count)
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
                    raise "json format reponse is unhandled - do you really need json?"
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
            # 400 returned on syntax error
            if response.status_code == 200:
                return response.content.decode('utf-8')
            show_retry_number(retry_count)
            sleep_before_retry(str(response.status_code) + " error code (response received)", api_url)
            continue
        except requests.exceptions.ConnectionError as e:
            print(e)
            show_retry_number(retry_count)
            sleep_before_retry("requests.exceptions.ConnectionError", api_url)
            continue
        except requests.exceptions.HTTPError as e:
            print(e.response.status_code)
            if e.response.status_code == 429 or e.response.status_code == 503:
                show_retry_number(retry_count)
                sleep_before_retry(e.response.status_code + " error code (HTTPError thrown)", api_url)
                continue
            raise e
        except requests.exceptions.ReadTimeout as e:
            time_now = time.time()
            time_used_for_query_in_s = time_of_query_start - time_now
            failure_explanation = "timeout (after " + str(time_used_for_query_in_s) + ", timeout passed to query was " + str(timeout) + " - if it is None then it defaulted to some value)"
            show_retry_number(retry_count)
            sleep_before_retry(failure_explanation, api_url)
            continue
        except requests.exceptions.ChunkedEncodingError as e:
            print(e)
            show_retry_number(retry_count)
            sleep_before_retry("requests.exceptions.ChunkedEncodingError", api_url)
            continue
        except urllib3.exceptions.ProtocolError as e:
            print(e)
            show_retry_number(retry_count)
            sleep_before_retry("urllib3.exceptions.ProtocolError", api_url)
            continue
        retry_count += 1
    print("overpass query failed!")

def parse_overpass_query_to_get_timeout(query):
    if ";" not in query:
        print("no ; in query so also no config header...")
        return
    query = query.split(";")[0]
    # now it should be reduced to something like:
    # [out:xml][timeout:1000];

    if "timeout" not in query:
        print("no timeout in query so also no timeout config")
        return
    query = query[query.find("timeout"):]
    #print("snipped query:", query)
    # now it should be reduced to something like:
    # timeout:1000];
    if ":" not in query:
        return
    query = query.split(":")[1]
    # now it should be reduced to something like:
    # 1000];
    #print("snipped query:", query)
    if "]" not in query:
        return
    query = query.split("]")[0]
    # now it should be reduced to something like:
    # 1000
    #print("snipped query:", query)
    print("timeout:", int(query))
    return int(query)

def single_query_run(api_url, query, timeout, user_agent, extra_info=None):
    print("downloading " + query)
    if timeout == None:
        print("Timeout in osm_bot_abstraction_layer.overpass_downloader.single_query_run was not specified! Trying to parse the query text to obtain it")
        print("query")
        print(query)
        print()
        print("parsing attempt")
        timeout = parse_overpass_query_to_get_timeout(query)
        if timeout == None:
            print("parsing failed, defaulting to 60 seconds")
            timeout = 60
        print(timeout)
        print()
        print()
        print()
    else:
        print("timeout specified to be ", timeout)
    print("download is now started, with timeout", timeout, "at", datetime.now())
    response = requests.post(
        api_url,
        data={'data': query},
        timeout=timeout,
        headers={'User-Agent': user_agent}
    )
    print("download completed with", response.status_code, "http code")
    if extra_info != None:
        print(extra_info)
    return response
