import idx_converter
import datetime
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from collections import defaultdict
import json
from _printer import (print_dict, print_list)


URL_BASE = 'https://www.sec.gov/Archives/'

DESIRED_INDUSTRY_GROUPS = ['Other', 'Computers', 'Telecommunications', 'Other Technology', 'Biotechnology', 'Other Health Care', 'Other Real Estate']
DESIRED_ENTITY_TYPES = ['Limited Liability Company', 'Corporation']
DESIRED_SECURITY_TYPES = ['isEquityType', 'isDebtType']


def get_idx_url(startingdt=None, endingdt=None):
    # returns a list of sub url for company idx requested
    # No datetime specified: idx for yesterday
    # 1 datetime specified: idx for specified date
    # 2 datetime specified: idx inside the range (implicitly requires endingdate > startigndate)
    urls = []
    if startingdt is None:
        dt = datetime.datetime.now() - datetime.timedelta(days=1)
        url = URL_BASE + 'edgar/daily-index/' + str(dt.year) +'/QTR' + str((dt.month-1)//3 + 1) + '/company.' + str(dt.year) + '%02d' % (dt.month) + '%02d' % (dt.day) + '.idx'
        urls.append(url)
    elif endingdt is None:
        dt = startingdt
        url = URL_BASE + 'edgar/daily-index/' + str(dt.year) +'/QTR' + str((dt.month-1)//3 + 1) + '/company.' + str(dt.year) + '%02d' % (dt.month) + '%02d' % (dt.day) + '.idx'
        urls.append(url)
    else:
        if endingdt < startingdt:
            return []
        date_list = [endingdt - datetime.timedelta(days=x) for x in range(0, (endingdt - startingdt).days)]
        for dt in date_list:
            url = URL_BASE + 'edgar/daily-index/' + str(dt.year) +'/QTR' + str((dt.month-1)//3 + 1) + '/company.' + str(dt.year) + '%02d' % (dt.month) + '%02d' % (dt.day) + '.idx'
            urls.append(url)
    return urls


def etree_to_dict(t):
    # turns a xml etree to a dict object
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v)
                        for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d

    
def get_data(start=None, end=None):
    # returns a list of dict for every form D submitted to SEC in the date range
    # if no date supplied, return data for yesterday
    # if only one date supplied, return data for that date

    result_list = []
    
    # Download idx file
    for url in get_idx_url(start, end):
        try:
            response = urllib.request.urlopen(url)
            f = response.read()
        except:
            print('exception when accessing ' + url)
            continue

        # construct the file url list
        try:
            form_list = idx_converter.read_file(f)
        except:
            print('error when processing ' + url)
            continue
        
        #iterate through every file
        for header in form_list:
            url = URL_BASE + header['file_name']
            print('Accessing ', url)
            try:
                formfile = urllib.request.urlopen(url).read()
                # concat xml part
                try:
                    formfile = formfile.decode('utf-8').split('</XML>')[0].split('<XML>\n')[1]
                except UnicodeDecodeError:
                    formfile = formfile.decode('latin-1').split('</XML>')[0].split('<XML>\n')[1]
                except:
                    print('decode failure when accessing ' + url)
                root = ET.fromstring(formfile)
                item = (etree_to_dict(root))
                if not item['edgarSubmission']['testOrLive'] == 'LIVE':
                    continue
                if not item['edgarSubmission']['offeringData']['industryGroup']['industryGroupType'] in DESIRED_INDUSTRY_GROUPS:
                    # print 'removing for industryGroup'
                    continue
                if not item['edgarSubmission']['primaryIssuer']['entityType'] in DESIRED_ENTITY_TYPES:
                    # print 'removing for entityType'
                    continue
                if set(item['edgarSubmission']['offeringData']['typesOfSecuritiesOffered'].keys()).isdisjoint(DESIRED_SECURITY_TYPES):
                    # print 'removing for security_type'
                    continue

                if isinstance(item['edgarSubmission']['relatedPersonsList']['relatedPersonInfo'], list):
                    for personInfo in item['edgarSubmission']['relatedPersonsList']['relatedPersonInfo']:
                        del personInfo['relatedPersonAddress']
                elif isinstance(item['edgarSubmission']['relatedPersonsList']['relatedPersonInfo'], dict):
                    del item['edgarSubmission']['relatedPersonsList']['relatedPersonInfo']['relatedPersonAddress']
                    item['edgarSubmission']['relatedPersonsList']['relatedPersonInfo'] = [item['edgarSubmission']['relatedPersonsList']['relatedPersonInfo']]
                else:
                    continue

                result_list.append({
                    'header': header,
                    'data': item
                })
            except:
                print('exception when accessing ' + url)
                continue
    return result_list

def main():
    for item in get_data():
        print_dict(item, 0)


if __name__ == '__main__':
    main()
    
