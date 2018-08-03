from auto_update import get_data
from _printer import print_list
import datetime


DESIRED_INDUSTRY_GROUPS = ['Other', 'Computers', 'Telecommunications', 'Other Technology', 'Biotechnology', 'Other Health Care', 'Other Real Estate']
DESIRED_ENTITY_TYPES = ['Limited Liability Company', 'Corporation']
DESIRED_SECURITY_TYPES = ['', ]

def main(start=None, end=None):
    rawdata = get_data(start, end)
    data = []
    for item in rawdata:
        print item['header']['company']
        if not item['data']['edgarSubmission']['testOrLive'] == 'LIVE':
            continue
        if not item['data']['edgarSubmission']['offeringData']['industryGroup'] in DESIRED_INDUSTRY_GROUPS:
            print 'removing for industryGroup'
            continue
        if not item['data']['edgarSubmission']['primaryIssuer']['entityType'] in DESIRED_ENTITY_TYPES:
            print 'removing for entityType'
            continue
        if set(item['data']['edgarSubmission']['offeringData']['typesOfSecuritiesOffered'].keys()).isdisjoint(DESIRED_SECURITY_TYPES):
            print 'removing for security_type'
            continue

        if isinstance(item['data']['edgarSubmission']['relatedPersonsList'], list):
            for personInfo in item['data']['edgarSubmission']['relatedPersonsList']['relatedPersonInfo']:
                del personInfo['relatedPersonAddress']
        elif isinstance(item['data']['edgarSubmission']['relatedPersonsList'], dict):
            del item['data']['edgarSubmission']['relatedPersonsList']['relatedPersonAddress']
        else:
            continue

        data.append(item)
    print_list(data, 0)


if __name__ == '__main__':
    end = datetime.datetime.now() - datetime.timedelta(days=1)
    start = end - datetime.timedelta(days=2)
    main(start, end)
