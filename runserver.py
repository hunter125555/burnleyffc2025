import os
from angular_flask import app
from apscheduler.schedulers.background import BackgroundScheduler
from manage import update_live_points, update_for_gw


def runserver():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
	sched = BackgroundScheduler()
	sched.add_job(update_for_gw, 'cron', day_of_week='sat-sun', hour='7', minute='30', timezone='America/New_York')
	sched.add_job(update_live_points, 'cron', day_of_week='sat-sun', hour='8-16', minute='0-59/10', timezone='America/New_York')
	sched.start()
	runserver()
