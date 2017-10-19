from apscheduler.schedulers.background import BackgroundScheduler
from manage import update_live_points, update_for_gw, update_test

sched = BackgroundScheduler()

@sched.scheduled_job('interval', minutes = 1)
def test_job():
	update_test()

#sched.add_job(update_for_gw, 'cron', day_of_week='sat-sun', hour='7', minute='30', timezone='America/New_York')
#sched.add_job(update_live_points, 'cron', day_of_week='sat-sun', hour='8-16', minute='0-59/10', timezone='America/New_York')
sched.start()
