from apscheduler.schedulers.blocking import BlockingScheduler
from manage import update_live_points, update_for_gw, update_test

sched = BlockingScheduler()

# @sched.scheduled_job('cron', day_of_week='wed-sun', hour='23', minute='38-43/1', timezone='America/New_York')
# def test_job():
# 	update_test()

@sched.scheduled_job('cron', day_of_week='sat-sun', hour='8-17/3', timezone='America/New_York')
def update_gw_data():
	update_for_gw()

@sched.scheduled_job('cron', day_of_week='sat-sun', hour='8-14', minute='0-59/10', timezone='America/New_York')
def update_live():
	update_live_points()

@sched.scheduled_job('cron', day_of_week='fri', hour='15-19/2', timezone='America/New_York')
def update_early_gw_data():
	update_for_gw()

sched.start()
