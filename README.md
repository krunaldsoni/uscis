# USCIS case status and neighbor watch
## Purpose
  * To find given case status and also check nearest neighbors case status of same type of application
## Motivation
  * My friend and my receipt number was 50 numbers apart like LIN2090012345 (my friend) and mine LIN2090012395
    * He got his EAD 3 weeks before I got, so I was using this script to pull the status of my neighbor through this script
    * It is crazy to find that USCIS was approving 2 applications per day from my range.
## Did I write from scratch
  * No but good amount of chunk is re-written, basically I combined multiple good uscis scripts on githubs and formated such a way that it is scalable in future
# Usage
## To find 10 neighbor before and 10 neighbor after the case id
 * _track_uscis_case_status.py  <USCIS_case_number>_
   * Note: It will count neighbors only when matching case type (I-140, I-765, I-131, I-485) is found
## To find given number of neighbors around case id
 * _track_uscis_case_status.py  <USCIS_case_number> -n 10_
### example

***py tracker_uscis.py LIN2190061752 -n 5***

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
