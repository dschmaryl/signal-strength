#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup


STATUS_URL = 'http://192.168.100.1/cgi-bin/status_cgi'


def get_strengths():
    try:
        source = requests.get(STATUS_URL, timeout=5)
        tables = BeautifulSoup(source.text, 'html.parser').find_all('table')
        status = tables[-1].find_all('tr')[2].find_all('td')[2].text
    except OSError:
        return {'error': 'no route to host'}
    except requests.exceptions.Timeout:
        return {'error': 'timed out'}
    except IndexError:
        return {'error': 'could not get status'}

    if status != 'Up':
        return {'error': 'wan connection is down'}

    # parse table for the strength/snr at each frequency
    rows = tables[1].find_all('tr')[1:]
    strengths, noise_ratios = [], []
    for row in rows:
        cells = row.find_all('td')
        strengths.append(float(cells[3].text.split()[0]))
        noise_ratios.append(float(cells[4].text.split()[0]))

    return {'strengths': strengths, 'noise_ratios': noise_ratios}


def average(input_list):
    return round(sum(input_list)/len(input_list), 2)


if __name__ == "__main__":
    results = get_strengths()
    if results.get('error'):
        print('ERROR: ' + results['error'])
    else:
        print('signal avg: %.2f dB' % average(results.get('strengths')))
        print('   snr avg: %.2f dB' % average(results.get('noise_ratios')))
