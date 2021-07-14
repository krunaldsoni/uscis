#!/usr/bin/env python

#*************************************************************************
#  External Package Needed: (Runs on Python3)
#   -> pip3 install BeautifulSoup4
#*************************************************************************
import re
import json
from pprint import pprint
from bs4 import BeautifulSoup
import os.path
import requests
from bs4 import BeautifulSoup as bs
import sys
import random
import re
import argparse
import time
import os, ssl
import warnings

#*************************************************************************
#  Lets Supress un-necessary HTTPS warnnings as we can trust USCIS website
#*************************************************************************
def supress_https_warnings():
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

def requestStatus(caseID):
    formData={"changeLocale":None,"completedActionsCurrentPage":0,"upcomingActionsCurrentPage":0,"appReceiptNum":caseID,"caseStatusSearchBtn":"CHECK STATUS"}
    response = requests.post('https://egov.uscis.gov/casestatus/mycasestatus.do',data=formData, verify=False)
    soup=bs(response.content, "html.parser" )
    #msg=soup.select("div form div div div div div div.rows.text-center p")[0].get_text()
    time.sleep(2)
    return soup
    
#*************************************************************************
#  DB is used to prevent bombarding USCIS server for un-necessary queries 
#*************************************************************************
def open_db():
    dataBase = {}
    visited = {}
    if os.path.isfile('data.txt'):
      with open('data.txt') as infile:
        dataBase = json.load(infile)
    if os.path.isfile('visited.txt'):
      with open('visited.txt') as infile:
        visited = json.load(infile)
    return dataBase, visited

def store_db(dataBase, visited):
    # store data
    with open('data.txt', 'w') as outfile:
      json.dump(dataBase, outfile)
    with open('visited.txt', 'w') as outfile:
      json.dump(visited, outfile)

#*************************************************************************
#  This will Query your case status and return find form type, so it will
#  help matching data relevant to your form type 
#*************************************************************************
def query_uscis_and_find_type_of_form(caseID):
    soup = requestStatus(caseID)
    formtype = ""
    for status in soup.findAll('div', {'class': 'rows text-center'}):
        if 'Form I-485' in status.text:
            formtype = "Form I-485"
        elif 'Form I-765' in status.text:
            formtype = "Form I-765"
        elif 'Form I-131' in status.text:
            formtype = "Form I-131"
        elif 'Form I-140' in status.text:
            formtype = "Form I-140"
    print(formtype)
    return formtype

#*************************************************************************
#  This Iterate through neighbors and match the given form-type and it'll
#  stop once we reached number provided to set how many neighbors to visit
#*************************************************************************
def query_uscis_based_on_form_type(dataBase, visited, caseID, formType, numRange):
    myCaseNum = int(re.sub("[^0-9]", "", caseID))
    myCenter = re.sub(r'[0-9]', "", caseID)
    # query USCIS check my case webpage
    for n in range (0-numRange, numRange):
      caseNum = str(myCaseNum + n)
      if caseNum not in visited:
        #soup = requestStatusUsingBrowserMethod('LIN' + caseNum)
        soup = requestStatus(myCenter + caseNum)
        # get current case status
        for status in soup.findAll('div', {'class': 'rows text-center'}):
          if all (keyWord in status.text for keyWord in [formType]):
            print(status.text)
            visited[caseNum] = 'visited'
            receiptNum = re.search('%s(\d+)'%myCenter, status.text).group(1)
            if 'Fingerprint Fee Was Received' in status.text:
              dataBase[receiptNum] = 'Fingerprint Fee Was Received'
            elif 'Case Was Approved' in status.text:
              dataBase[receiptNum] = 'Case Was Approved'
            elif any (deny in status.text for deny in ['Case Was Rejected', 'Decision Notice Mailed']):
              dataBase[receiptNum] = 'Case Rejected'
            elif 'Case Was Received' in status.text:
              dataBase[receiptNum] = 'Case Received'
            elif 'Case Is Ready To Be Scheduled For An Interview' in status.text:
              dataBase[receiptNum] = 'Ready for Interview'
            elif any (RFE in status.text for RFE in ['Request for Additional Evidence Was Mailed', 'Request For Evidence Was Received']):
              dataBase[receiptNum] = 'RFE'
            elif 'Case Was Transferred' in status.text:
              dataBase[receiptNum] = 'Case Transferred'
            elif 'Name Was Updated' in status.text:
              dataBase[receiptNum] = 'Name Updated'
            elif 'Fingerprints Were Taken' in status.text:
                dataBase[receiptNum] = 'Fingerprints Taken'

def count_entries_from_db(dataBase):
    numTotalCase = 0
    numApproved = 0
    numRejected = 0
    numFPReceived = 0
    numReceived = 0
    numInterview = 0
    numRFE = 0
    numTransfer = 0
    numNameUpdated = 0
    FingerPrintTaken = 0

    for case in dataBase:
      numTotalCase += 1
      if dataBase[case]=='Fingerprint Fee Was Received':
        numFPReceived += 1
      elif dataBase[case]=='Case Was Approved':
        numApproved += 1
      elif dataBase[case]=='Case Rejected':
        numRejected += 1
      elif dataBase[case]=='Case Received':
        numReceived += 1
      elif dataBase[case]=='Ready for Interview':
        numInterview += 1
      elif dataBase[case]=='RFE':
        numRFE += 1
      elif dataBase[case]=='Case Transferred':
        numTransfer += 1
      elif dataBase[case]=='Name Updated':
        numNameUpdated += 1
      elif dataBase[case]=='Fingerprints Taken':
        FingerPrintTaken += 1
    return numTotalCase, numApproved, numRejected, numFPReceived, numReceived, numInterview, numRFE, numTransfer, numNameUpdated, FingerPrintTaken

def print_database_entries(template, caseID, numTotalCase, numApproved, numRejected, numFPReceived, numReceived, numInterview, numRFE, numTransfer, numNameUpdated, FingerPrintTaken):
    print('*********************************')
    print('For ' + str(2*numRange) + ' neighbors of ' + caseID +', we found the following statistics: ')
    print(template.format('total number of I-485 application received: ', str(numTotalCase)))
    print(template.format('Case Was Approved: ', str(numApproved)))
    print(template.format('Fingerprint taken: ', str(FingerPrintTaken)))
    print(template.format('Fingerprint Fee Was Received: ', str(numFPReceived)))
    print(template.format('Case Was Rejected: ', str(numRejected)))
    print(template.format('Case Was Received: ', str(numReceived)))
    print(template.format('Case Was Ready for Interview: ', str(numInterview)))
    print(template.format('Case is RFE: ', str(numRFE)))
    print(template.format('Case Was Transferred: ', str(numTransfer)))
    print(template.format('Name Was Updated: ', str(numNameUpdated)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('RecieptNumber', help='Your USCIS Reciept Number, starts with 3 letters', default='')
    parser.add_argument('-n', type=int, metavar='N', nargs='?', const=10 ,help='Enable Neighbour Polling, followed by # of neighbour to check, default is 10')
    args = parser.parse_args()
    supress_https_warnings()
    #initial hardcoded data
    caseID = args.RecieptNumber
    numRange = int(args.n)
    dataBase = {}
    visited = {}
    #main work
    dataBase, visited = open_db()
    formType = query_uscis_and_find_type_of_form(caseID)
    query_uscis_based_on_form_type(dataBase, visited, caseID, formType, numRange)
    store_db(dataBase, visited)
    numTotalCase, numApproved, numRejected, numFPReceived, numReceived, numInterview, numRFE, numTransfer, numNameUpdated, FingerPrintTaken = count_entries_from_db(dataBase)
    template = '{0:45}{1:5}'
    print_database_entries(template, caseID, numTotalCase, numApproved, numRejected, numFPReceived, numReceived, numInterview, numRFE, numTransfer, numNameUpdated, FingerPrintTaken)
