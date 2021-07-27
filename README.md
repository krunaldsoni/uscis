# USCIS case status and neighbor watch
## Purpose
  * To find given case status and also check nearest neighbors case status of same type of application
## External Packages needed
  * pip3 install BeautifulSoup4 json2html APScheduler
## Motivation
  * My friend and my receipt number was 50 numbers apart like LIN2090012345 (my friend) and mine LIN2090012395
    * He got his EAD 3 weeks before I got, so I was using this script to pull the status of my neighbor through this script
    * It is crazy to find that USCIS was approving 2 applications per day from my range.
## Did I write from scratch
  * No but good amount of chunk is re-written, basically I combined multiple good uscis scripts on githubs and formated such a way that it is scalable in future
## Usage
  * usage to get individual case status:
  ***track_uscis_case_status.py --case <case_number>***
  * usage to get individual case and its neighbors with same case type:
  ***track_uscis_case_status.py --case <case_number> --check  <howmany_neighbors to check>***
  * usage to get report of all forms type in this range:
  ***track_uscis_case_status.py --range  <start_number> <end_number>***
### example

***py tracker_uscis.py --case LIN2190061752 --check 5***

Checks 5 neighbors before target number and 5 neighbors after
```
=====Your Case Status=====
Your case-id: LIN2190061752    Form-Type: Form I-140


Case Was Approved And My Decision Was Emailed
We approved your Form I-140, Immigrant Petition for Alien Worker, Receipt Number LIN2190061752, and emailed you an approval notice.  Please follow any instructions on the approval notice.  If you move, go to www.uscis.gov/addresschange  to give us your new mailing address.

==============================
For 10 neighbors of LIN2190061752, we found the following statistics:
total number of Form I-140  application received: 2
Case Was Approved:                           2
Fingerprint taken:                           0
Fingerprint Fee Was Received:                0
Case Was Rejected:                           0
Case Was Received:                           0
Case Was Ready for Interview:                0
Case is RFE:                                 0
Case Was Transferred:                        0
Name Was Updated:                            0
```

***py tracker_uscis.py --range LIN2190061752 LIN2190061758***
```
Checks the entire range and publish html file containing data in table format.
```

### How to deploy on Heroku
 * If you are looking to deploy this on heroku (AWS like service) then you need crontab or scheduler to fire python script which crawl every fixed hours
 * Once crawl is completed, html will be generated and that html should be placed in to template folder.
 * To generate Scheduler, follow: https://saqibameen.com/deploy-python-cron-job-scripts-on-heroku/ 
