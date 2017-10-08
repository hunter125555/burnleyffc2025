import os
import json
import argparse
import requests

from angular_flask.core import db
from angular_flask.models import Post
from angular_flask.core import mongo

from angular_flask import app
from angular_flask import helper

teamList = ['Arsenal', 'Brighton', 'Bournemouth', 'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Huddersfield', 'Leicester', 'Liverpool', 'Man City',  'Man Utd', 'Newcastle', 'Southampton', 'Stoke', 'Swansea', 'Spurs', 'Watford', 'West Brom', 'West Ham']
team_folder = os.path.join(os.getcwd(),'teams')
static_url = 'https://fantasy.premierleague.com/drf/bootstrap-static'

def soupify(url):
	htmltext = requests.get(url)
	data = htmltext.json()
	return data

static_data = soupify(static_url)

def update_current_gw():
	with app.app_context():
		currentgw = mongo.db.currentgw
		eid = currentgw.find_one()['_id']
		gw = static_data['current-event']
		currentgw.find_one_and_update({'_id': eid}, {'$set': {'gw': gw}})

def update_epl_teams():
	with app.app_context():
		eplteams = mongo.db.eplteams
		eplteams.insert_many([{'name': str(team['name']), 'short': str(team['short_name']), 'id': team['id']} for team in static_data['teams']])

def update_epl_players():
	with app.app_context():
		eplplayers = mongo.db.eplplayers
		eplplayers.insert_many([{'id': str(player['id']), 'name': player['web_name'], 'team': player['team']} for player in static_data['elements']])

# def update_epl_playerteams():
# 	with app.app_context():
# 		eplplayerteams = mongo.db.eplplayerteams
# 		eplplayerteams.insert_many([{str(player['id']): player['team']} for player in static_data['elements']])

def update_fpl_managers():
	with app.app_context():
		fplmanagers = mongo.db.fplmanagers
		for team in teamList:
			team = team.lower() + ".txt"
			team_file = os.path.join(team_folder, team)
			team_name, ffc_team = helper.read_in_team(team_file)
			codenametuples = [(player[1][1], player[1][0]) for player in ffc_team.items()]
			fplmanagers.insert_many([{'code': str(tup[0]), 'name': tup[1]} for tup in codenametuples])

def update_ffcteams():
	with app.app_context():
		ffcteams = mongo.db.ffcteams
		for team in teamList:
			teamfile= team.lower() + ".txt"
			team_file = os.path.join(team_folder, teamfile)
			team_name, ffc_team = helper.read_in_team(team_file)
			fplcodes = [player[1][1] for player in ffc_team.items()]
			ffcteams.insert_one({'team':team, 'codes': fplcodes})

def update_gw_fixtures():
	with app.app_context():
		gwfixtures = mongo.db.gwfixtures
		gwfixtures.delete_many({})
		gw = mongo.db.currentgw.find_one()['gw']
		live_url = 'https://fantasy.premierleague.com/drf/event/%d/live' % gw
		live_data = soupify(live_url)
		gwfixtures.insert_many({'id': str(fix['id']), 'started': fix['started']} for fix in live_data['fixtures'])

def update_live_points():
	with app.app_context():
		livepoints = mongo.db.livepoints
		livepoints.delete_many({})
		gw = mongo.db.currentgw.find_one()['gw']
		live_url = 'https://fantasy.premierleague.com/drf/event/%d/live' % gw
		live_data = soupify(live_url)['elements']
		livepoints.insert_many({'id': str(player[0]), 'points': player[1]['stats']['total_points']} for player in live_data.items())

def update_ffc_picks():
	with app.app_context():
		ffcteams = mongo.db.ffcteams
		ffcpicks = mongo.db.ffcpicks
		ffcpicks.delete_many({})
		gw = mongo.db.currentgw.find_one()['gw']
		for team in teamList:
			obj = ffcteams.find_one({'team': team})
			for code in obj['codes']:
				picks_url = 'https://fantasy.premierleague.com/drf/entry/%d/event/%d/picks' % (code, gw)
				gw_data = soupify(picks_url)
				playing, bench = [], []
				captain = None
				vicecaptain = None
				chip = gw_data['active_chip']
				transcost = gw_data['entry_history']['event_transfers_cost']
				for pick in gw_data['picks']:
					if pick['is_captain']:
						captain = pick['element']
					if pick['is_vice_captain']:
						vicecaptain = pick['element']
					if pick['position'] >= 12:
						bench.append(pick['element'])
					else:
						playing.append(pick['element'])
				ffcpicks.insert_one({'captain': captain, 'vicecaptain': vicecaptain, 'chip': chip, 'cost': transcost, 'playing': playing, 'bench': bench})
				#import code; code.interact(local=locals())

# def update_ffc_captains():


def main():
	parser = argparse.ArgumentParser(
		description='Manage this Flask application.')
	parser.add_argument(
		'command', help='the name of the command you want to run')
	args = parser.parse_args()

	if args.command == 'update_gw':
		update_current_gw()
		print "GW Updated!"
	elif args.command == 'update_eplteams':
		update_epl_teams()
		print "EPL Teams added!"
	elif args.command == 'update_eplplayers':
		update_epl_players()
		print "EPL Players added!"
	# elif args.command == 'update_eplplayers_teams':
	# 	update_epl_playerteams()
	# 	print "EPL Playerteams added!"
	elif args.command == 'update_fplmanagers':
		update_fpl_managers()
		print "FPL Managers added!"
	elif args.command == 'update_ffcteams':
		update_ffcteams()
		print "FFC Teams added!"
	elif args.command == 'update_gwfixtures':
		update_gw_fixtures()
		print "GW Fixtures added!"
	elif args.command == 'update_live_points':
		update_live_points()
		print "Live points added!"
	elif args.command == 'update_ffc_picks':
		update_ffc_picks()
		print "FFC picks added!"
	else:
		raise Exception('Invalid command')

if __name__ == '__main__':
	main()
