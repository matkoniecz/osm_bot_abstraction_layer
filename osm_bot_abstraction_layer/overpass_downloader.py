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

def get_response_from_overpass_server(query, timeout, user_agent):
    #print("sleeping before download")
    #sleep(20)
    time_of_query_start = None
    retry_count = -1
    while True:
        retry_count += 1
        try:
            # https://wiki.openstreetmap.org/wiki/Overpass_API#Public_Overpass_API_instances
            # tried to track official documentation but failed
            # see https://github.com/drolbr/overpass-doc/issues/16 for basically asking about this
            # see https://github.com/drolbr/overpass-doc/pull/15 for a probing PR
            main_api_url = "https://overpass-api.de/api/interpreter"
            api_url = random.choice([main_api_url])
            print("using", api_url)

            time_of_query_start = time.time()
            if retry_count>0:
                response = single_query_run(api_url, query, timeout, user_agent, "retry number " + str(retry_count))
            else:
                response = single_query_run(api_url, query, timeout, user_agent, "the first attempt")
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
                if "[out:json]" in query or "[out:csv]" in query:
                    print("json and cvs format response is unhandled - do you really need json or csv? See https://overpass-turbo.eu/s/1mjM for an example of a silently failing query") #TODO: put also link to this community thread
                response_length = len(response.content.decode('utf-8'))
                print("response length:", response_length)
                # very long indicates that data was returned, some may be some massive that parsing would be outrageously expensive
                if response_length < 10_000 and "[out:json]" not in query and "[out:csv]" not in query:
                    parsed = lxml.etree.fromstring(response.content) # yes, without .decode('utf-8')
                    if parsed.find('remark') != None:
                        raise Exception('timeout in query or other failure!' + query)


            # 429 and 503 indicate rate limiting
            # 504 appears to be a bug https://github.com/drolbr/Overpass-API/issues/220
            # 400 returned on syntax error
            # TODO: repeating queries as fast as Overpass allows is fine, as long as you sleep after being hit by 429
            # so you can follow /status and make queries more often than done now
            # see also https://dev.overpass-api.de/overpass-doc/en/preface/commons.html
            # drolbr (admin of main public overpass instance):
            # "The rate limit 429 asks the client to slow down. The HTTP 503 informs the client that 
            # there is little it can do because the server is overloaded."
            # "See https://dev.overpass-api.de/overpass-doc/en/preface/commons.html . Maybe we should link to that page more prominently. 
            # I'm also open to rephrase it to make it clearer that only careless people are a problem."
            # "A very good rule of thumb is: when you have many any precautions for responding to overload then you
            # do not cause critical overload."
            if response.status_code == 200:
                return response.content.decode('utf-8')
            sleep_before_retry(str(response.status_code) + " error code (response received)", api_url)
            continue
        except requests.exceptions.ConnectionError as e:
            print(e)
            sleep_before_retry("requests.exceptions.ConnectionError", api_url)
            continue
        except requests.exceptions.HTTPError as e:
            print(e.response.status_code)
            # from IRC by drolbr running main public Overpass servers:
            # 503 tells you that the server is so busy that it will not reliably accept queries from anyone
            # 429 tells you that your current usage in that minute is so relatively high that the server
            # throttles you in favour of other users
            if e.response.status_code == 429 or e.response.status_code == 503:
                sleep_before_retry(e.response.status_code + " error code (HTTPError thrown)", api_url)
                continue
            raise e
        except requests.exceptions.ReadTimeout as e:
            time_now = time.time()
            time_used_for_query_in_s = time_now - time_of_query_start
            failure_explanation = "timeout (after " + str(time_used_for_query_in_s) + ", timeout passed to query was " + str(timeout) + " - if it is None then it defaulted to some value)"
            sleep_before_retry(failure_explanation, api_url)
            continue
        except requests.exceptions.ChunkedEncodingError as e:
            print(e)
            sleep_before_retry("requests.exceptions.ChunkedEncodingError", api_url)
            continue
        # for example
        # ConnectionResetError(104, 'Connection reset by peer')
        # not sure is it happening on poor connection or explicit request by server
        # to slow down, in either case waiting a bit is a good idea
        except urllib3.exceptions.ProtocolError as e:
            print(e)
            sleep_before_retry("urllib3.exceptions.ProtocolError", api_url)
            continue
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
    # now it should be reduced to something like:
    # timeout:1000];
    if ":" not in query:
        return
    query = query.split(":")[1]
    # now it should be reduced to something like:
    # 1000];
    if "]" not in query:
        return
    query = query.split("]")[0]
    # now it should be reduced to something like:
    # 1000
    return int(query)

def single_query_run(api_url, query, timeout, user_agent, extra_info=None):
    print("single_query_run: downloading " + query)
    if timeout == None:
        timeout = parse_overpass_query_to_get_timeout(query)
        if timeout == None:
            raise Exception("parsing for timeout failed (and it was not specified)")
        print("Timeout in osm_bot_abstraction_layer.overpass_downloader.single_query_run was not specified! According to parsing it is", timeout)
        print()
    else:
        print("timeout specified to be ", timeout)
    time = datetime.now()
    print("download is now started, with timeout", timeout, "at", time)
    response = requests.post(
        api_url,
        data={'data': query},
        timeout=timeout,
        headers={'User-Agent': user_agent}
    )
    print("download completed with", response.status_code, "http code at", datetime.now(), "after", str(datetime.now()-time) )
    if extra_info != None:
        print(extra_info)
    return response
