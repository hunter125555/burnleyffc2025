import os
import json
import argparse
import requests

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
		print 'Updated GW!'

def update_epl_teams():
	with app.app_context():
		eplteams = mongo.db.eplteams
		eplteams.insert_many([{'name': str(team['name']), 'short': str(team['short_name']), 'id': team['id']} for team in static_data['teams']])

def update_epl_players():
	with app.app_context():
		eplplayers = mongo.db.eplplayers
		eplplayers.insert_many([{'id': str(player['id']), 'name': player['web_name'], 'team': player['team']} for player in static_data['elements']])

def update_fpl_managers():
	with app.app_context():
		fplmanagers = mongo.db.fplmanagers
		fplmanagers.delete_many({})
		for team in teamList:
			team = team.lower() + ".txt"
			team_file = os.path.join(team_folder, team)
			team_name, ffc_team = helper.read_in_team(team_file)
			codenametuples = [(player[1][1], player[1][0]) for player in ffc_team.items()]
			fplmanagers.insert_many([{'code': str(tup[0]), 'name': tup[1]} for tup in codenametuples])

def update_ffcteams():
	with app.app_context():
		ffcteams = mongo.db.ffcteams
		ffcteams.delete_many({})
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
		gwfixtures.insert_many({'id': str(fix['id']), 'started': fix['started'], 'home': fix['team_h'], 'away': fix['team_a']} for fix in live_data['fixtures'])

def update_live_points():
	with app.app_context():
		print 'Updating!'
		livepoints = mongo.db.livepoints
		livepoints.delete_many({})
		gw = mongo.db.currentgw.find_one()['gw']
		live_url = 'https://fantasy.premierleague.com/drf/event/%d/live' % gw
		live_data = soupify(live_url)['elements']
		livepoints.insert_many({'id': str(player[0]), 'fixture': player[1]['explain'][0][1], 'points': player[1]['stats']['total_points']} for player in live_data.items())
		print 'Updated!'

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
				points = gw_data['entry_history']['points']
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
				ffcpicks.insert_one({'code': code, 'points': points, 'captain': captain, 'vicecaptain': vicecaptain, 'chip': chip, 'cost': transcost, 'playing': playing, 'bench': bench})
 
def update_ffc_captains():
	with app.app_context():
		ffccaptains = mongo.db.ffccaptains
		capCodes = [2447194, 264776, 121748, 613856, 718230, 81684, 861138, 715890, 20074, 303886, 480417, 1783450, 1155448, 641656, 234593, 668092, 541178, 44187, 469030, 514199]
		for team, capcode in zip(teamList, capCodes):
			ffccaptains.insert_one({'team': team, 'captain': capcode})

def update_ffc_bench():
	with app.app_context():
		ffcbench = mongo.db.ffcbench
		benchCodes = [944016, 1002200, 1214, 1447559, 767012, 556122, 672855, 99293, 683730, 3383, 674118, 1788203, 773359, 80362, 147565, 540557, 886572, 948427, 9306, 765882]
		for team, bcode in zip(teamList, benchCodes):
			ffcbench.insert_one({'team': team, 'bench': bcode})

def update_for_gw():
	update_current_gw()
	update_gw_fixtures()
	update_live_points()
	update_ffc_picks()

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
	elif args.command == 'update_ffc_captains':
		update_ffc_captains()
		print "FFC captains added!"
	elif args.command == 'update_ffc_bench':
		update_ffc_bench()
		print "FFC bench updated!"
	elif args.command == 'update_for_gw':
		update_for_gw()
		print "Update for GW complete!"
	else:
		raise Exception('Invalid command')

if __name__ == '__main__':
	main()
