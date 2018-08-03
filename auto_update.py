import idx_converter
import datetime
import urllib2
import xml.etree.ElementTree as ET
from collections import defaultdict
import json
from _printer import (print_dict, print_list)


URL_BASE = 'https://www.sec.gov/Archives/'


def get_idx_url(startingdt=None, endingdt=None):
    # returns a list of sub url for company idx requested
    # No datetime specified: idx for yesterday
    # 1 datetime specified: idx for specified date
    # 2 datetime specified: idx inside the range (implicitly requires endingdate > startigndate)
    urls = []
    if startingdt is None:
        dt = datetime.datetime.now() - datetime.timedelta(days=1)
        url = URL_BASE + 'edgar/daily-index/' + str(dt.year) +'/QTR' + str(dt.month/3 + 1) + '/company.' + str(dt.year) + '%02d' % (dt.month) + '%02d' % (dt.day) + '.idx'
        urls.append(url)
    elif endingdt is None:
        dt = startingdt
        url = URL_BASE + 'edgar/daily-index/' + str(dt.year) +'/QTR' + str(dt.month/3 + 1) + '/company.' + str(dt.year) + '%02d' % (dt.month) + '%02d' % (dt.day) + '.idx'
        urls.append(url)
    else:
        if endingdt < startingdt:
            return []
        date_list = [endingdt - datetime.timedelta(days=x) for x in xrange(0, (endingdt - startingdt).days)]
        for dt in date_list:
            url = URL_BASE + 'edgar/daily-index/' + str(dt.year) +'/QTR' + str(dt.month/3 + 1) + '/company.' + str(dt.year) + '%02d' % (dt.month) + '%02d' % (dt.day) + '.idx'
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
            response = urllib2.urlopen(url)
            f = response.read()
        except:
            print 'exception when accessing ' + url
            return result_list

        # construct the file url list
        form_list = idx_converter.read_file(f)
    
        #iterate through every file
        for item in form_list:
            url = URL_BASE + item['file_name']
            formfile = urllib2.urlopen(url).read()
            # concat xml part
            formfile = formfile.split('</XML>')[0].split('<XML>\n')[1]
            root = ET.fromstring(formfile)
            d = (etree_to_dict(root))
            result_list.append({
                'header': item,
                'data': d
            })

    return result_list

def main():
    for item in get_data():
        print_dict(item, 0)


if __name__ == '__main__':
    main()
    
