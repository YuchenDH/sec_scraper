from auto_update import get_data
from _printer import print_list, print_dict
import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta


def main(start=None, end=None):
    rawdata = get_data(start, end)
    data = []
    for item in rawdata:
        if not item['data']['edgarSubmission']['testOrLive'] == 'LIVE':
            continue
        if not item['data']['edgarSubmission']['offeringData']['industryGroup']['industryGroupType'] in DESIRED_INDUSTRY_GROUPS:
            # print 'removing for industryGroup'
            continue
        if not item['data']['edgarSubmission']['primaryIssuer']['entityType'] in DESIRED_ENTITY_TYPES:
            # print 'removing for entityType'
            continue
        if set(item['data']['edgarSubmission']['offeringData']['typesOfSecuritiesOffered'].keys()).isdisjoint(DESIRED_SECURITY_TYPES):
            # print 'removing for security_type'
            continue

        if isinstance(item['data']['edgarSubmission']['relatedPersonsList']['relatedPersonInfo'], list):
            for personInfo in item['data']['edgarSubmission']['relatedPersonsList']['relatedPersonInfo']:
                del personInfo['relatedPersonAddress']
        elif isinstance(item['data']['edgarSubmission']['relatedPersonsList']['relatedPersonInfo'], dict):
            del item['data']['edgarSubmission']['relatedPersonsList']['relatedPersonInfo']['relatedPersonAddress']
            item['data']['edgarSubmission']['relatedPersonsList']['relatedPersonInfo'] = [item['data']['edgarSubmission']['relatedPersonsList']['relatedPersonInfo']]
        else:
            continue

        data.append(item)

    tabledata = []
    for row in data:
        tablerow = {}
        tablerow['CIK'] = row['header']['CIK']
        tablerow['Company'] = row['header']['company']
        tablerow['Form Type'] = row['header']['form_type']
        tablerow['Date Filed'] = row['header']['date_filed']
        tablerow['File Name'] = row['header']['file_name']
        
        tablerow['JurisdictionOfInc'] = row['data']['edgarSubmission']['primaryIssuer']['jurisdictionOfInc']
        tablerow['Entity Type'] = row['data']['edgarSubmission']['primaryIssuer']['entityType']
        tablerow['Since'] = row['data']['edgarSubmission']['primaryIssuer']['yearOfInc'].get('value', 'Over 5 years')
        tablerow['relatedPersons'] = []
        for person in row['data']['edgarSubmission']['relatedPersonsList']['relatedPersonInfo']:
            newperson = {}
            newperson['Name'] = person['relatedPersonName']['firstName'] + ' ' +  person['relatedPersonName']['lastName']
            newperson['Relationships'] = person['relatedPersonRelationshipList']['relationship']
            tablerow['relatedPersons'].append(newperson)
        tablerow['Industry Group'] = row['data']['edgarSubmission']['offeringData']['industryGroup']['industryGroupType']
        tablerow['Issuer Size'] = row['data']['edgarSubmission']['offeringData']['issuerSize']['revenueRange']
        tablerow['Is Amendment'] = row['data']['edgarSubmission']['offeringData']['typeOfFiling']['newOrAmendment']['isAmendment']
        tablerow['Date of First Sale'] = row['data']['edgarSubmission']['offeringData']['typeOfFiling']['dateOfFirstSale'].get('value', None)
        tablerow['Duration of Offering More than One Year'] = row['data']['edgarSubmission']['offeringData']['durationOfOffering']['moreThanOneYear']
        tablerow['Types of Securities Offered'] = row['data']['edgarSubmission']['offeringData']['typesOfSecuritiesOffered'].keys()
        tablerow['Min Investment Accepted'] = row['data']['edgarSubmission']['offeringData']['minimumInvestmentAccepted']
        tablerow['Sales Compensation List'] = row['data']['edgarSubmission']['offeringData']['salesCompensationList']
        tablerow['Total Offering Amount'] = row['data']['edgarSubmission']['offeringData']['offeringSalesAmounts']['totalOfferingAmount']
        tablerow['Total Amount Sold'] = row['data']['edgarSubmission']['offeringData']['offeringSalesAmounts']['totalAmountSold']
        tablerow['Total Remaining'] = row['data']['edgarSubmission']['offeringData']['offeringSalesAmounts']['totalRemaining']
        tablerow['Clarification of Sales Amounts'] = row['data']['edgarSubmission']['offeringData']['offeringSalesAmounts']['clarificationOfResponse']
        tablerow['Has Non-Accredited Investors'] = row['data']['edgarSubmission']['offeringData']['investors']['hasNonAccreditedInvestors']
        tablerow['Total Number of Inversters Already Invested'] = row['data']['edgarSubmission']['offeringData']['investors']['totalNumberAlreadyInvested']
        tabledata.append(tablerow)

    table = pd.DataFrame.from_dict(tabledata)

    return table

if __name__ == '__main__':
    end = datetime.datetime.now() - datetime.timedelta(days=1)
    start = end - relativedelta(years=20)
    main(start, end)
