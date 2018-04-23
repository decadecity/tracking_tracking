from ua_parser import user_agent_parser
from urllib.parse import urlparse, parse_qs
import re
import copy

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

base_result = {
    'total': 0,
    'do_not_track': {
        '0': 0,
        '1': 0,
    },
    'google_analytics': {
        '0': 0,
        '1': 0,
    },
    'matomo': {
        '0': 0,
        '1': 0,
    },
    'tag_manager': {
        '0': 0,
        '1': 0,
    },
}

oss = {}
browsers = {}

android = copy.deepcopy(base_result)
ios = copy.deepcopy(base_result)
other_os = copy.deepcopy(base_result)

firefox = copy.deepcopy(base_result)
chrome = copy.deepcopy(base_result)
safari = copy.deepcopy(base_result)
other_browser = copy.deepcopy(base_result)

def add_result_to(result_set, result):
    result_set['total'] += 1
    result_set['do_not_track'][result['qs']['d'][0]] += 1
    result_set['google_analytics'][result['qs']['g'][0]] += 1
    result_set['matomo'][result['qs']['m'][0]] += 1
    result_set['tag_manager'][result['qs']['t'][0]] += 1


def process_result(match):
    result = {}
    ua = user_agent_parser.Parse(match.group('user_agent'))
    os = ua['os']['family']
    browser = ua['user_agent']['family']

    result['os'] = os
    result['browser'] = browser

    oss[os] = oss.get(os, 0) + 1
    browsers[browser] = browsers.get(browser, 0) + 1

    url = urlparse(match.group('request').split()[1])
    qs = parse_qs(url.query)
    result['qs'] = qs

    add_result_to(base_result, result)
    if os == 'Android':
        add_result_to(android, result)
    elif os == 'iOS':
        add_result_to(ios, result)
    else:
        add_result_to(other_os, result)
        if browser.startswith('Chrom'):
            add_result_to(chrome, result)
        elif browser.startswith('Firefox'):
            add_result_to(firefox, result)
        elif browser == 'Safari':
            add_result_to(safari, result)
        else:
            add_result_to(other_browser, result)


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

def process_result(result):
    output = {}
    total = result['total']
    output['total'] = total

    dnt = round(result['do_not_track']['1']/total*100, 1)
    output['do_not_track_enabled'] = dnt

    ga = round(result['google_analytics']['1']/total*100, 1)
    output['google_analytics_enabled'] = ga
    output['google_analytics_diff'] = round((100 - dnt) - ga, 1)

    matomo = round(result['matomo']['1']/total*100, 1)
    output['matomo_enabled'] = matomo
    output['matomo_diff'] = round((100 - dnt) - matomo, 1)

    gtm = round(result['tag_manager']['1']/total*100, 1)
    output['tag_manager_enabled'] = gtm
    output['tag_manager_diff'] = round((100 - dnt) - gtm, 1)

    print(output)

#print(oss)
#print(browsers)

print('== Base result ==================')
process_result(base_result)

print('== Android ==================')
process_result(android)
print('== iOS ==================')
process_result(ios)
print('== Other OS ==================')
process_result(other_os)

print('== Firefox ==================')
process_result(firefox)
print('== Chrome ==================')
process_result(chrome)
print('== Safari ==================')
process_result(safari)
print('== Other Browser ==================')
process_result(other_browser)

