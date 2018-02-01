import os
import json
import argparse
import requests
from collections import Counter, OrderedDict

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

def update_test():
	with app.app_context():
		test = mongo.db.test
		val = test.find_one()['val']
		test.find_one_and_update({'var': 'a'}, {'$set': {'val': val + 1}})


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
		eplplayers.delete_many({})
		eplplayers.insert_many([{'id': player['id'], 'name': player['first_name'] + ' ' + player['second_name'], 'team': player['team'], 'pos': player['element_type']} for player in static_data['elements']])

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
		#livepoints.insert_many({'id': str(player[0]), 'points': player[1]['stats']['total_points']} for player in live_data.items())
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
				try:
					gw_data = soupify(picks_url)
				except ValueError:
					print picks_url
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
		ffccaptains.delete_many({})
		capCodes = [5609, 5065, 9350, 223, 776734, 76521, 350414, 1167796, 683730, 16471, 7243, 970393, 559067, 85810, 220254, 667989, 155651, 224000, 7496, 663518]
		for team, capcode in zip(teamList, capCodes):
			ffccaptains.insert_one({'team': team, 'captain': capcode})

def update_ffc_bench():
	with app.app_context():
		ffcbench = mongo.db.ffcbench
		ffcbench.delete_many({})
		benchCodes = [237830, 4629, 90373, 613856, 1566657, 2307, 1535142, 3465481, 351798, 208003, 2658923, 44900, 262843, 3758662, 234593, 666138, 673387, 130215, 12927, 644991]
		for team, bcode in zip(teamList, benchCodes):
			ffcbench.insert_one({'team': team, 'bench': bcode})

def analyze_tx_history():
	with app.app_context():
		order_dict = lambda d: OrderedDict(sorted(d.items(), key = lambda x: x[1], reverse=True))
		eplplayers = mongo.db.eplplayers
		playerlist = list(eplplayers.find())
		tx_dict = dict()
		for player in playerlist:
			player_url = 'https://fantasy.premierleague.com/drf/element-summary/%d' % (player['id'])
			player_history = soupify(player_url)['history']
			tx_dict[player['name']] = 0
			for w in player_history:
				if w['transfers_balance'] >= 0:
					tx_dict[player['name']] += 1
				else:
					tx_dict[player['name']] -= 1
		import code; code.interact(local=locals())
		final_dict = order_dict(tx_dict)
		print take(20, final_dict.iteritems())

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
	elif args.command == 'tx':
		analyze_tx_history()
	elif args.command == 'test':
		update_test()
		print "Test pass!"
	else:
		raise Exception('Invalid command')

if __name__ == '__main__':
	main()
