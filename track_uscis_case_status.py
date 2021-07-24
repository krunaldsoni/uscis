#!/usr/bin/env python

#*************************************************************************
#  External Package Needed: (Runs on Python3)
#   -> pip3 install BeautifulSoup4 json2html
#*************************************************************************
import re
import json
from pprint import pprint
from bs4 import BeautifulSoup
import os.path
import requests
from bs4 import BeautifulSoup as bs
from json2html import *
import sys
import random
import re
import argparse
import time
import os, ssl
import warnings
import datetime

FORM_485 = "Form I-485"
database_485 = {}
FORM_765 = "Form I-765"
database_765 = {}
FORM_131 = "Form I-131"
database_131 = {}
FORM_140 = "Form I-140"
database_140 = {}
database = {}
DATA = "data.json"
SUMMARY = "summary.json"

FINGER_PRINT_FEE_RX       = 'Fingerprint Fee Was Received'
CASE_APPROVED             = 'Case Was Approved'
CASE_REJECTED             = 'Case Rejected'
CASE_RECEIVED             = 'Case Received'
INTERVIEW_READY           = 'Ready for Interview'
CASE_RFE                  = 'RFE'
CASE_TRANSFERRED          = 'Case Transferred'
NAME_UPDATED              = 'Name Updated'
FINGER_PRINT_TAKEN        = 'Fingerprints Taken'
INVALID_STATUS            = 'Invalid status'

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
    #time.sleep(2)
    return soup
    
#*************************************************************************
#  DB is used to prevent bombarding USCIS server for un-necessary queries 
#*************************************************************************
def write_to_file(db, file):
    # store data
    with open(file, 'w') as outfile:
      json.dump(db, outfile, indent=4)

def find_if_form_type_we_are_interested_in(formType):
    if (formType != FORM_485) and (formType != FORM_765) and (formType != FORM_140) and (formType != FORM_131):
        return 0
    return 1
    
def get_date():
    x = datetime.datetime.now()
    return x.strftime("%x")
    
def find_case_status(status):
    case_status = INVALID_STATUS
    if 'Fingerprint Fee Was Received' in status.text:
      case_status = FINGER_PRINT_FEE_RX
    elif 'Case Was Approved' in status.text:
      case_status = CASE_APPROVED
    elif any (deny in status.text for deny in ['Case Was Rejected', 'Decision Notice Mailed']):
      case_status = CASE_REJECTED
    elif 'Case Was Received' in status.text:
      case_status = CASE_RECEIVED
    elif 'Case Is Ready To Be Scheduled For An Interview' in status.text:
      case_status = INTERVIEW_READY
    elif any (RFE in status.text for RFE in ['Request for Additional Evidence Was Mailed', 'Request For Evidence Was Received']):
      case_status = CASE_RFE
    elif 'Case Was Transferred' in status.text:
      case_status = CASE_TRANSFERRED
    elif 'Name Was Updated' in status.text:
      case_status = NAME_UPDATED
    elif 'Fingerprints Were Taken' in status.text:
      case_status = FINGER_PRINT_TAKEN
    return case_status

#*************************************************************************
#  This will Query your case status and return find form type, so it will
#  help matching data relevant to your form type 
#*************************************************************************
def query_uscis_and_find_type_of_form(caseID, print_status):
    soup = requestStatus(caseID)
    formtype = ""
    status = ""
    db = database
    for status in soup.findAll('div', {'class': 'rows text-center'}):
        case_status = find_case_status(status)
        if FORM_485 in status.text:
            formtype = FORM_485
            db = database_485
        elif FORM_765 in status.text:
            formtype = FORM_765
            db = database_765
        elif FORM_131 in status.text:
            formtype = FORM_131
            db = database_131
        elif FORM_140 in status.text:
            formtype = FORM_140
            db = database_140
    #db[caseID] = case_status
    if print_status == 1:
        print("=====Your Case Status=====")
        print("Your case-id: %s    Form-Type: %s\n" % (caseID, formtype))
        print(status.text);
        print("==============================")
    return formtype, case_status, db

#*************************************************************************
#  This Iterate through neighbors and match the given form-type and it'll
#  stop once we reached number provided to set how many neighbors to visit
#*************************************************************************
def query_uscis_based_on_form_type(db, caseID, formType, numRange):
    myCaseNum = int(re.sub("[^0-9]", "", caseID))
    myCenter = re.sub(r'[0-9]', "", caseID)
    # query USCIS check my case webpage
    for n in range (0-numRange, numRange):
        caseNum = str(myCaseNum + n)
        #soup = requestStatusUsingBrowserMethod('LIN' + caseNum)
        soup = requestStatus(myCenter + caseNum)
        # get current case status
        for status in soup.findAll('div', {'class': 'rows text-center'}):
            if all (keyWord in status.text for keyWord in [formType]):
                #print(status.text)
                receiptNum = re.search('%s(\d+)'%myCenter, status.text).group(1)
                temp_case_id = myCenter + str(caseNum)
                db[temp_case_id] = find_case_status(status)
            

def count_entries_from_db(db):
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
    
    for case in db:
      numTotalCase += 1
      if db[case]==FINGER_PRINT_FEE_RX:
        numFPReceived += 1
      elif db[case]==CASE_APPROVED:
        numApproved += 1
      elif db[case]==CASE_REJECTED:
        numRejected += 1
      elif db[case]==CASE_RECEIVED:
        numReceived += 1
      elif db[case]==INTERVIEW_READY:
        numInterview += 1
      elif db[case]==CASE_RFE:
        numRFE += 1
      elif db[case]==CASE_TRANSFERRED:
        numTransfer += 1
      elif db[case]==NAME_UPDATED:
        numNameUpdated += 1
      elif db[case]==FINGER_PRINT_TAKEN:
        FingerPrintTaken += 1
    return numTotalCase, numApproved, numRejected, numFPReceived, numReceived, numInterview, numRFE, numTransfer, numNameUpdated, FingerPrintTaken

def print_database_entries(template, caseID, formType, numTotalCase, numApproved, numRejected, numFPReceived, numReceived, numInterview, numRFE, numTransfer, numNameUpdated, FingerPrintTaken):
    print('For ' + str(2*numRange) + ' neighbors of ' + caseID +', we found the following statistics: ')
    print(template.format('total number of %s  application received: ' % formType, str(numTotalCase)))
    print(template.format('Case Was Approved: ', str(numApproved)))
    print(template.format('Fingerprint taken: ', str(FingerPrintTaken)))
    print(template.format('Fingerprint Fee Was Received: ', str(numFPReceived)))
    print(template.format('Case Was Rejected: ', str(numRejected)))
    print(template.format('Case Was Received: ', str(numReceived)))
    print(template.format('Case Was Ready for Interview: ', str(numInterview)))
    print(template.format('Case is RFE: ', str(numRFE)))
    print(template.format('Case Was Transferred: ', str(numTransfer)))
    print(template.format('Name Was Updated: ', str(numNameUpdated)))

def do_check_my_case_my_neighbors(caseID, numRange):
    #initial hardcoded data
    db = {}
    #main work
    print_status = 1
    formType, case_status, db = query_uscis_and_find_type_of_form(caseID, print_status)
    query_uscis_based_on_form_type(db, caseID, formType, numRange)
    write_to_file(db, DATA)
    numTotalCase, numApproved, numRejected, numFPReceived, numReceived, numInterview, numRFE, numTransfer, numNameUpdated, FingerPrintTaken = count_entries_from_db(db)
    template = '{0:1}{1:5}'
    print_database_entries(template, caseID, formType, numTotalCase, numApproved, numRejected, numFPReceived, numReceived, numInterview, numRFE, numTransfer, numNameUpdated, FingerPrintTaken)

def dump_each_form_to_db(db, numTotalCase1, numApproved1, numRejected1, numFPReceived1, numReceived1, numInterview1, numRFE1, numTransfer1, numNameUpdated1, FingerPrintTaken1):
    db["Total Case"]             = numTotalCase1
    db["Case Received"]          = numReceived1
    db["Case Approved"]          = numApproved1
    db["Case Rejected"]          = numRejected1
    db["Finger fee received"]    = numFPReceived1
    db["Finger Print Taken"]     = FingerPrintTaken1
    db["Ready for Interview"]    = numInterview1
    db["RFE"]                    = numRFE1
    db["Case Transferred"]       = numTransfer1
    db["Name Was Updated"]       = numNameUpdated1
    return db
    
def count_each_db_and_draw_plot():
    db, db1, db2, db3, db4 = {}, {}, {}, {}, {}
    if database_485:
        numTotalCase1, numApproved1, numRejected1, numFPReceived1, numReceived1, numInterview1, numRFE1, numTransfer1, numNameUpdated1, FingerPrintTaken1 = count_entries_from_db(database_485)
        db[FORM_485] = dump_each_form_to_db(db1, numTotalCase1, numApproved1, numRejected1, numFPReceived1, numReceived1, numInterview1, numRFE1, numTransfer1, numNameUpdated1, FingerPrintTaken1)
    if database_131:
        numTotalCase2, numApproved2, numRejected2, numFPReceived2, numReceived2, numInterview2, numRFE2, numTransfer2, numNameUpdated2, FingerPrintTaken2 = count_entries_from_db(database_131)
        db[FORM_131] = dump_each_form_to_db(db2, numTotalCase2, numApproved2, numRejected2, numFPReceived2, numReceived2, numInterview2, numRFE2, numTransfer2, numNameUpdated2, FingerPrintTaken2)
    if database_765:
        numTotalCase3, numApproved3, numRejected3, numFPReceived3, numReceived3, numInterview3, numRFE3, numTransfer3, numNameUpdated3, FingerPrintTaken3 = count_entries_from_db(database_765)
        db[FORM_765] = dump_each_form_to_db(db3, numTotalCase3, numApproved3, numRejected3, numFPReceived3, numReceived3, numInterview3, numRFE3, numTransfer3, numNameUpdated3, FingerPrintTaken3)
    if database_140:
        numTotalCase4, numApproved4, numRejected4, numFPReceived4, numReceived4, numInterview4, numRFE4, numTransfer4, numNameUpdated4, FingerPrintTaken4 = count_entries_from_db(database_140)
        db[FORM_140] = dump_each_form_to_db(db4, numTotalCase4, numApproved4, numRejected4, numFPReceived4, numReceived4, numInterview4, numRFE4, numTransfer4, numNameUpdated4, FingerPrintTaken4)
    return db

def get_fonts():
    return "<link rel='preconnect' href='https://fonts.googleapis.com'> \
            <link rel='preconnect' href='https://fonts.gstatic.com' crossorigin> \
            <link href='https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@300&display=swap' rel='stylesheet'> "
def get_table_design():
    return ".row {\
              display: flex;\
              margin-left:-5px;\
              margin-right:-5px;\
            }\
            .column {\
              flex: 50%;\
              padding: 5px;\
            }"

def create_beautiful_html(db1, db2, range1, range2):
    HTML_FILE_NAME = 'summary.html'
    CSS_FILE_NAME  = 'summary.css'
    START_HTML     = "\n<html>\n"
    END_HTML       = "\n</html>\n"
    START_BODY     = "\n\t<body>\n"
    END_BODY       = "\n\t</body>\n"
    HEAD_HTML      = "\
                        \t<head>                                                                                           \n\
                        \t\t%s                                                                                             \n\
                        \t\t<style>                                                                                        \n\
                        \t\t\t body {                                                                                      \n\
                        \t\t\t\t font-family: 'Roboto Condensed', serif;                                                   \n\
                        \t\t\t\t font-size: 24px;                                                                          \n\
                        \t\t\t }                                                                                           \n\
                        \t\t\t %s                                                                                           \n\
                        \t\t</style>                                                                                       \n\
                        \t</head>                                                                                          \n\
                    " % (get_fonts(), get_table_design())
    BODY_TITLE_HTML = "\
                        \t\t<div><h1> USCIS Data: %s  Range: (%s : %s) (Tweeter: @krunal_7131)</h1></div>              \n\
                    " % (get_date(), range1, range2)
    
    attibute = " \"class=\"table table-bordered table-hover\"\" align=\"left\""
    BODY_CONTENT_GAP = "\n\n"
    #BODY_CONTENT = json2html.convert(json = db, table_attributes = attibute)
    CONTENT = "<div class='row'>"
    for (k, v) in db2.items():
        CONTENT += "\n<div class='column'>"
        CONTENT += "\n" + "<h2>" + k + "</h2>" + "\n"
        CONTENT += "\t" + json2html.convert(json = v, table_attributes = attibute)
        CONTENT += "\n</div>"
    CONTENT += "\n</div>"
    summary_html = open("summary.html", "w")  # append mode
    summary_html.write(START_HTML + HEAD_HTML + START_BODY + BODY_TITLE_HTML + BODY_CONTENT_GAP + CONTENT + END_BODY + END_HTML)
    summary_html.close()
    json_html = open("data.html", "w")  # append mode
    #BODY_CONTENT = json2html.convert(json = db)
    json_html.write(START_HTML + HEAD_HTML + START_BODY + BODY_TITLE_HTML + json.dumps(db1) + END_BODY + END_HTML)
    json_html.close()
    
def do_check_case_range(range1, range2):
    db, temp_db = {}, {}
    temp1_db = {}
    range1_num = int(re.sub("[^0-9]", "", range1))
    range2_num = int(re.sub("[^0-9]", "", range2))
    myCenter = re.sub(r'[0-9]', "", range1)
    # query USCIS check my case webpage
    for n in range (range1_num, range2_num):
        caseID = myCenter + str(n)
        print_status = 0
        formType, case_status, db = query_uscis_and_find_type_of_form(caseID, print_status)
        db[caseID] = case_status
        if find_if_form_type_we_are_interested_in(formType) == 1:
            temp_db[formType] = db
    write_to_file(temp_db, DATA)
    temp1_db = count_each_db_and_draw_plot()
    write_to_file(temp1_db, SUMMARY)
    create_beautiful_html(temp_db, temp1_db, range1, range2)


def get_args(argv):
    case = ""
    check = 0
    range1 = ""
    range2 = ""
    if  len(argv) == 1:
        print("usage to get individual case status: \n             track_uscis_case_status.py --case <case_number>")
        print("usage to get individual case and its neighbors with same case type: \n             track_uscis_case_status.py --case <case_number> --check  <howmany_neighbors to check>")
        print("usage to get report of all forms type in this range: \n             track_uscis_case_status.py --range  <start_number> <end_number>")
        exit()

    for arg in range(1, len(argv)):
        if argv[arg] == "--case":
            print("case number given")
            if len(argv) > (arg + 1):
                case = argv[arg+1]
                #validate case here
                if len(argv) > (arg + 2):
                    if argv[arg + 2] == "--check":
                        if len(argv) > (arg + 3):
                            check = int(argv[arg + 3])
                        else:
                            print("missing case number after --check")
            else:
                print("missing case number after --case")
                exit()
        elif argv[arg] == "--range":
            if len(argv) == 4:
                range1 = argv[arg+1]
                range2 = argv[arg+2]
                myrange1 = int(re.sub("[^0-9]", "", range1))
                myrange2 = int(re.sub("[^0-9]", "", range2))
                if range1 > range2:
                    print("first provide lower number than higher number")
                    exit()
            else:
                print("missing path name after --range")
                exit()
    return case, check, range1, range2


    
if __name__ == "__main__":
    caseID, numRange, range1, range2 = get_args(sys.argv)
    supress_https_warnings()
    if (numRange !=0) and (caseID != ""):
        do_check_my_case_my_neighbors(caseID, numRange)
    else:
        do_check_case_range(range1, range2)
