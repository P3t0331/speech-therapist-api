from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django.utils.timezone import timedelta
from django_apscheduler.models import DjangoJobExecution
import sys

from core.models import User, TaskResult

# This is the function you want to schedule - add as many as you want and then register them in the start() function below
def check_daystreak():
    patients = User.objects.filter(is_therapist=False)
    today = timezone.now().date()
    for patient in patients:
        patient_last_result = patient.last_result_posted
        if not patient_last_result:
            patient.day_streak = 0
            patient.save()
            continue
        last_result_date = patient_last_result.date()
        if last_result_date < today - timedelta(days=1):
            patient.day_streak = 0
            patient.save()


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # run this job every 24 hours
    scheduler.add_job(check_daystreak, trigger=CronTrigger(hour="00", minute="00"), id='check_daystreak', name='check_daystreak', jobstore='default', replace_existing=True)
    register_events(scheduler)
    scheduler.start()
    print("Scheduler started...", file=sys.stdout)