import schedule
import time as tm
from DB import check_modification
import os


def job():
    check_modification()

schedule.every(10).seconds.do(job)

def run_scheduler():
    while True:
        schedule.run_pending()
        tm.sleep(1)

run_scheduler()




  