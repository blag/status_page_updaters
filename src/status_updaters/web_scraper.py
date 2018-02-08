"""
This script scrapes web pages for status text and reports the parsed status to a central status
server.

The only supported configuration mechanism is through environment variables.

  STATUS_SERVER_REPORT_STATUS_URL
    The full URL of the central status server to HTTP POST status results to
    Example: https://status.addsrv.com/events/slack/events

    If REPORT_STATUS_URL is empty, a default value will be used:

        https://{STATUS_SERVER_FQDN}/services/{STATUS_SERVER_SERVICE_SLUG}/events

    Those variables are interpolated from environment variables:

      STATUS_SERVER_FQDN
        The FQDN of the central status server, used only if REPORT_STATUS_URL is False-y
        Example: status.addsrv.com
      STATUS_SERVER_SERVICE_SLUG
        The slug of the service to report status
        Example: slack

  STATUS_SERVER_API_KEY
    The API key from the status server - usually a bot token
    Example: eyJ0e..o-FLc

  SERVICE_STATUS_URL
    The URL of the service's external webpage
    Example: https://status.slack.com

  SERVICE_STATUS_HTML_SELECTOR
    The pyQuery (look it up, it's cool) CSS/HTML selector that selects the appropriate element from
    the status webpage. The selected element will be converted to text with '.text()'.
    Example: #current_status h1

  EXPECTED_STATUS_UP_TEXT
  EXPECTED_STATUS_DOWN_TEXT
    This is the text used to compare against the selected element from the status webpage. If a
    direct comparison is not successful, the script will fallback to checking against regexes.
    When regexes are used, the script adds additional capture information in the 'extra' key of the
    POSTed data.
"""
import inspect
import os
import re
import sys

from urllib.request import urlopen

import requests

from certifi import where as ca_file
from pyquery import PyQuery as pq


try:
    REPORT_STATUS_URL = os.environ.get('STATUS_SERVER_REPORT_STATUS_URL')  # https://status.addsrv.com

    if REPORT_STATUS_URL is None:
        REPORT_STATUS_URL = "https://{status_server_fqdn}/services/{service_slug}/events".format(
            status_server_fqdn=os.environ['STATUS_SERVER_FQDN'],  # status.addsrv.com
            service_slug=os.environ['STATUS_SERVER_SERVICE_SLUG'])  # slack

    STATUS_SERVER_API_KEY = os.environ['STATUS_SERVER_API_KEY'].replace('\n', '')

    SERVICE_STATUS_URL = os.environ['SERVICE_STATUS_URL']  # 'https://status.slack.com'

    SERVICE_STATUS_HTML_SELECTOR = os.environ['SERVICE_STATUS_HTML_SELECTOR']  # '#current_status h1'

    EXPECTED_STATUS_UP_TEXT = os.environ['EXPECTED_STATUS_UP_TEXT']  # 'Smooth sailing!'
    EXPECTED_STATUS_DOWN_TEXT = os.environ.get('EXPECTED_STATUS_DOWN_TEXT')
except KeyError:
    print(inspect.getdoc(sys.modules[__name__]))
    raise


d = pq(url=SERVICE_STATUS_URL, opener=lambda url: urlopen(url, cafile=ca_file()).read())

status = d(SERVICE_STATUS_HTML_SELECTOR).text()

data = {
    'description': status,
    'informational': False,
}

if status == EXPECTED_STATUS_UP_TEXT:
    print(f"Got expected 'up' status: {status}")
    data['status'] = "up"
elif EXPECTED_STATUS_DOWN_TEXT and status == EXPECTED_STATUS_DOWN_TEXT:
    print(f"Got expected 'down' status: {status}")
    data['status'] = "down"
else:
    print("Matching status against regexes")

    data['extra'] = {
        "notes": "The status was extracted from the webpage text and may not be "
                 "completely accurate.",
        "actual_text": status,
    }

    # There are multiple ways to fail, so we check for different words
    up_match = re.search(r'\b(?P<status>smooth sailing|up|all systems go|(?:no|zero) (?:issues?|problems?)|operating normally)\b', status, re.IGNORECASE)

    if up_match is not None:
        print(f"Matched 'up' status: {up_match.group('status')}")
        data['status'] = "up"
        data['extra']['matched_text'] = up_match.group('status')
    else:
        down_match = re.search(r'\b(?P<status>trouble|down|some systems|difficulty|(?:issues?|problems?)|non-operational)\b', status, re.IGNORECASE)
        if down_match is not None:
            print(f"Matched 'down' status: {down_match.group('status')}")
            data['status'] = "down"
            data['extra']['matched_text'] = down_match.group('status')
        else:
            # If we can't reasonably guess, just exit
            print("Cannot reasonably guess at status, exiting")
            sys.exit(-1)

response = requests.post(REPORT_STATUS_URL, headers={'Authorization': f"JWT {STATUS_SERVER_API_KEY}"}, json=data)

print(response.text)
