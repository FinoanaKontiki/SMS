import sms
import sms.views
from sms import app
import  atexit

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger

if __name__ == "__main__":
        scheduler = BackgroundScheduler(timezone="Europe/Berlin")
        trigger = OrTrigger([CronTrigger(day_of_week='Mon-Sat', hour=9, minute=35)])
        scheduler.add_job(sms.views.lunch, trigger)
        scheduler.start()
        #Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())
        
        app.run(debug=True, port=5016)
