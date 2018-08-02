import idx_converter
import datetime
import xml.etree.ElementTree as ET
from collections import defaultdict
import json


URL_BASE = 'https://www.sec.gov/Archives/'


def get_idx_url(dt=datetime.datetime.now()):
    url = URL_BASE + 'edgar/daily-index/' + str(dt.year) +'/QTR' + str(dt.month/3 + 1) + '/company.' + str(dt.year) + '%02d' % (dt.month) + '%02d' % (dt.day - 1) + '.idx'
    return url


def etree_to_dict(t):
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


def print_dict(d, indent):
    if not isinstance(d, dict):
        print d
    print '{'
    for k, v in d.items():
        for i in xrange(indent+1):
            print ' ',
        print k + ':',
        if isinstance(v, dict):
            print_dict(v, indent+1)
        elif isinstance(v, list):
            print_list(v, indent+1)
        else:
            print repr(v) + ','
    for i in xrange(indent):
        print ' ',
    print '}'


def print_list(l, indent):
    if not isinstance(l, list):
        print l
    print '['
    for v in l:
        for i in xrange(indent+1):
            print ' ',
        if isinstance(v, dict):
            print_dict(v, indent+1)
        elif isinstance(v, list):
            print_list(v, indent+1)
        else:
            print  repr(v) + ','
    for i in xrange(indent):
        print ' ',
    print ']'

    
def update():
    # Download idx file
    import urllib2
    response = urllib2.urlopen(get_idx_url())
    f = response.read()

    # construct the file url list
    form_list = idx_converter.read_file(f)

    #iterate through every file
    for item in form_list:
        url = URL_BASE + item['file_name']
        print 'Accessing ' + url
        formfile = urllib2.urlopen(url).read()
        # concat xml part
        formfile = formfile.split('</XML>')[0].split('<XML>\n')[1]
        root = ET.fromstring(formfile)
        d = (etree_to_dict(root))
        print_dict(d, 0)
        

def main():
    update()


if __name__ == '__main__':
    main()
    
