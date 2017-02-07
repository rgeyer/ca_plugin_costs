import requests,logging,json,os,csv

from requests import *
from datetime import *

config = {}
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
session = Session()

def oauth_authentication():
    uri = "https://{}/api/oauth2".format(config["shard"])
    data = {
        "refresh_token": config["oauth_refresh_token"],
        "grant_type": "refresh_token"
    }
    headers = {"X-Api-Version": "1.5"}
    headers["content-type"] = "application/json"
    response = session.post(uri, headers=headers, data=json.dumps(data))
    print_request(response)
    response_json_obj = json.loads(response.text)
    config["access_token"] = response_json_obj["access_token"]
    return response_json_obj


def send_request(method, url, data=False):
    uri = "https://analytics.rightscale.com{}".format(url)
    headers = {"X-Api-Version": "1.0", "content-type": "application/json"}
    if "access_token" in config:
        headers["Authorization"] = "Bearer {}".format(config["access_token"])
    response = getattr(session, method.lower())(uri, data=data, headers=headers)

    return response


def print_request(response):
    logger.debug('{}\n{}\n{}\n\n{}'.format(
        '-----------REQUEST-----------',
        response.request.method + ' ' + response.request.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in response.request.headers.items()),
        response.request.body,
    ))


    logger.debug('{}\n{}\n\n{}'.format(
        '-----------RESPONSE-----------',
        '\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
        response.text,
    ))


# Entrypoint is here...
if os.path.isfile("config.json"):
    with open('config.json', 'r') as f:
        config_text = f.read()

    config = json.loads(config_text)

    response = oauth_authentication()
    # response = send_request("POST", "/api/cloud_bills/actions/filter_options", data=json.dumps({'start_time': "2016-01-01T00:00:00", 'end_time': "2016-01-30T00:00:00", 'filter_types': ["cloud_bill:account_id"]}))
    # print_request(response)

    with open('Plugin Cost Data - Sheet1.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            datetimeobj = datetime.strptime(str(row[3]),"%m/%d/%Y")
            datetimestr = datetimeobj.strftime("%Y-%m-%dT00:00:00")
            datajson = {"start_time": datetimestr, "account_href": "/api/accounts/30601", "total_cost": row[2], "product": row[0], "product_category": row[4]}
            datastr = json.dumps(datajson)
            response = send_request("POST", "/api/plugin_costs", data=datastr)
            print_request(response)
else:
    print "gotta has config"
