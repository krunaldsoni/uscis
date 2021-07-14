# uscis

Combined multiple good uscis scripts on githubs and formated such a way that it is scalable in future

# Usage
## To find 10 neighbor before and 10 neighbor after the case id
 * track_uscis_case_status.py  <USCIS_case_number>
   * Note: It will count neighbors only when matching case type (I-140, I-765, I-131, I-485) is found
## To find given number of neighbors around case id
 * track_uscis_case_status.py  <USCIS_case_number> -n 10
### example

py tracker_uscis.py LIN2190061752 -n 10

Checks 10 neighbors before target number and 10 neighbors after
```
*********************************
For 20 neighbors of LIN2190061752, we found the following statistics:
total number of I-140 application received:  4
Case Was Approved:                           1
Fingerprint taken:                           0
Fingerprint Fee Was Received:                0
Case Was Rejected:                           0
Case Was Received:                           3
Case Was Ready for Interview:                0
Case is RFE:                                 0
Case Was Transferred:                        0
Name Was Updated:                            0
```
