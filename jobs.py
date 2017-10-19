from apscheduler.schedulers.blocking import BlockingScheduler
from manage import update_live_points, update_for_gw, update_test

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='wed-sun', hour='23', minute='38-43/1', timezone='America/New_York')
def test_job():
	update_test()

# @sched.scheduled_job('cron', day_of_week='sat-sun', hour='7', minute='30', timezone='America/New_York')
# def update_gw_data():
# 	update_for_gw()

# @sched.scheduled_job('cron', day_of_week='sat-sun', hour='8-16', minute='0-59/10', timezone='America/New_York')
# def update_live():
# 	update_live_points()

sched.start()
