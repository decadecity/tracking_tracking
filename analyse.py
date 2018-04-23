from ua_parser import user_agent_parser
from urllib.parse import urlparse, parse_qs
import re

from pprint import pprint as print

format_pat= re.compile(
    r"(?P<host>[\d\.]+)\s"
    r"(?P<identity>\S*)\s"
    r"(?P<user>\S*)\s"
    r"\[(?P<time>.*?)\]\s"
    r'"(?P<request>.*?)"\s'
    r"(?P<status>\d+)\s"
    r"(?P<bytes>\S*)\s"
    r'"(?P<referer>.*?)"\s' # [SIC]
    r'"(?P<user_agent>.*?)"\s*'
)

result = []
oss = {}
browsers = {}

def process_result(match):
    item = {}
    ua = user_agent_parser.Parse(match.group('user_agent'))
    os = ua['os']['family']
    browser = ua['user_agent']['family']

    item['os'] = os
    item['browser'] = browser

    oss[os] = oss.get(os, 0) + 1
    browsers[browser] = browsers.get(browser, 0) + 1

    url = urlparse(match.group('request').split()[1])
    qs = parse_qs(url.query)
    item['qs'] = qs
    result.append(item)

for day in range(45):
    with open('logs/tracking-result.access.log.{}'.format(day)) as logfile:
        line_no = 0
        for line in logfile.readlines():
            line_no += 1
            match = format_pat.match(line)
            if not match:
                raise KeyError('Mismatch at line {} of {}'.format(line_no, day))
            else:
                process_result(match)

print(oss)
print(browsers)
