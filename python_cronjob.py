########################################
# Package Scheduler.
# install : "pip3 install APScheduler"
# Purpose: Very useful while deploying on heroku
#######################################
import os
from apscheduler.schedulers.blocking import BlockingScheduler
SCHEDULE_FREQ_IN_SECONDS = 60
SCHEDULE_FREQ_IN_HOURS   = 24


def system_commands():
    os.system("python track_uscis_case_status.py --range LIN2190069000 LIN2190069020")

# Create an instance of scheduler and add function.
scheduler = BlockingScheduler()
scheduler.add_job(system_commands, "interval", seconds=SCHEDULE_FREQ_IN_SECONDS)

scheduler.start()
