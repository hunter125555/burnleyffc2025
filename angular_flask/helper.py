import requests
import json
import os
from collections import Counter, OrderedDict
import math

from angular_flask.core import mongo

teamList = ['Arsenal', 'Brighton', 'Bournemouth', 'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Huddersfield', 'Leicester', 'Liverpool', 'Man City',  'Man Utd', 'Newcastle', 'Southampton', 'Stoke', 'Swansea', 'Spurs', 'Watford', 'West Brom', 'West Ham']
team_folder = os.path.join(os.getcwd(),'teams')
all_data_url = 'https://fantasy.premierleague.com/drf/bootstrap-static'
dynamic_url = 'https://fantasy.premierleague.com/drf/bootstrap-dynamic'
flatten = lambda l: [item for sublist in l for item in sublist]
order_dict = lambda d: OrderedDict(sorted(d.items(), key = lambda x: x[1], reverse=True))

def soupify(url):
	htmltext = requests.get(url)
	data = htmltext.json()
	return data

def standard_deviation(lst):
	num_items = len(lst)
	mean = sum(lst) / num_items
	differences = [x - mean for x in lst]
	sq_differences = [d ** 2 for d in differences]
	ssd = sum(sq_differences)
	variance = float(ssd) / float(num_items)
	return round(math.sqrt(variance), 2)

def get_current_gw():
	return mongo.db.currentgw.find_one()['gw']

def get_ffc_players(team_name):
	fplmanagers = mongo.db.fplmanagers
	ffcteams = mongo.db.ffcteams
	fplcodes = ffcteams.find_one({'team': team_name})['codes']
	player_names = []
	for code in fplcodes:
		player_names.append(fplmanagers.find_one({'code': str(code)})['name'])
	return player_names

def read_in_team(filename):
	player_no = 1
	player_code_table = {}
	target = open(filename, 'r')
	for line in target:
		if ',' not in line:
			team_name = line.strip()
			continue
		else:
			line = line.split(',')
			player_name = line[0]
			player_url = line[1].strip()
			player_id = [int(num) for num in line[1].split('/') if num.isdigit()][0]
			player_code_table[player_no] = (player_name, player_id, player_url)
			player_no+=1
	target.close()
	return team_name, player_code_table

def get_current_team(fplcode, include_fpl_captain_twice = False, exclude = False):
	gw = get_current_gw()
	current_team, bench, teamcount = [], [], []
	ffcpicks = mongo.db.ffcpicks
	picks = ffcpicks.find_one({'code': fplcode})
	eplplayers = mongo.db.eplplayers
	livepoints = mongo.db.livepoints
	gwfixtures = mongo.db.gwfixtures
	for pick in picks['playing']:
		if exclude:
			fixid = livepoints.find_one({'id': str(pick)})['fixture']
			if gwfixtures.find_one({'id': str(fixid)})['started']:
				continue
		current_team.append(pick)
		teamcount.append(eplplayers.find_one({'id': pick})['team'])
		if pick == picks['captain'] and include_fpl_captain_twice:
			current_team.append(pick)
			if picks['chip'] == "3xc":
				current_team.append(pick)
	for pick in picks['bench']:
		if exclude:
			fixid = livepoints.find_one({'id': str(pick)})['fixture']
			if gwfixtures.find_one({'id': str(fixid)})['started']:
				continue
		bench.append(pick)
		teamcount.append(eplplayers.find_one({'id': pick})['team'])
	if picks['chip'] == "bboost":
		current_team += bench
	return current_team, bench, teamcount

def get_ffcteamdetails(team_name, ffc_captain = -1, ffc_bench = -1, include_fpl_captain_twice = False, include_fpl_bench=False, exclude = False, team_count = False, consider_ffc_bench = False):
	team_details, team_count_details = [], []
	ffcteams = mongo.db.ffcteams
	eplteams = mongo.db.eplteams
	eplplayers = mongo.db.eplplayers
	fpl_codes = ffcteams.find_one({'team': team_name})['codes']
	gw = get_current_gw()
	ffccaptains = mongo.db.ffccaptains
	ffcbench = mongo.db.ffcbench
	ffc_captain = ffccaptains.find_one({'team': team_name})['captain']
	fpl_codes.append(ffc_captain)
	if consider_ffc_bench:
		if ffc_bench != -1:
			del fpl_codes[ffc_bench]
		else:
			ffc_bench = ffcbench.find_one({'team': team_name})['bench']
			del fpl_codes[fpl_codes.index(ffc_bench)]
	for fcode in fpl_codes:
		current, bench, teamcount = get_current_team(fcode, include_fpl_captain_twice, exclude)
		team_details.append(current)
		team_count_details.append(teamcount)
		if include_fpl_bench:
			team_details.append(bench)
	team_details = flatten(team_details)
	total_player_count = dict(Counter(team_details))
	total_player_count_sorted = order_dict(dict((eplplayers.find_one({'id': k})['name'], v) for k,v in total_player_count.items()))
	if team_count:
		team_count_details = flatten(team_count_details)
		total_team_count = dict(Counter(team_count_details))
		total_teamname_count = {}
		for k, v in total_team_count.items():
			name = eplteams.find_one({'id': k})['short']
			total_teamname_count[name] = v
		total_team_count_sorted = order_dict(total_teamname_count)
		final_dict = OrderedDict()
		for k, v in total_player_count_sorted.items() + total_team_count_sorted.items():
			final_dict[k] = v
		return final_dict
	else:
		return total_player_count_sorted

def get_differentials(t1,t2):
	players_both_sides = set(list(t1.keys()) + list(t2.keys()))
	diff = {key: t1.get(key, 0) - t2.get(key, 0) for key in players_both_sides}
	diff_sorted = order_dict(diff)
	return diff_sorted

def get_live_points(entry_code, live = True):
	gw_score = 0
	ffcpicks = mongo.db.ffcpicks
	livepoints = mongo.db.livepoints
	picks = ffcpicks.find_one({'code': entry_code})
	if not live:
		return picks['points'] - picks['cost']
	if picks['chip'] == 'bboost':
		picks['playing'] += picks['bench']
	cap = picks['captain']
	pickpoints = []
	for pick in picks['playing']:
		points = livepoints.find_one({'id': str(pick)})['points']
		pickpoints.append(points)
		if picks['chip'] == '3xc' and pick == cap:
			pickpoints.append(points)
			pickpoints.append(points)
		elif pick == cap:
			pickpoints.append(points)
	gw_score = sum(pickpoints)
	transfer_cost = picks['cost']
	live_score = gw_score - transfer_cost
	return live_score

def team_scoreboard(team_name, gw = -1, live = True):
	if gw == -1: gw = get_current_gw()
	ffcpicks = mongo.db.ffcpicks
	fplmanagers = mongo.db.fplmanagers
	ffcteams = mongo.db.ffcteams
	fpl_codes = ffcteams.find_one({'team': team_name})['codes']
	scores = []
	points, transfer_costs = [], []
	player_urls = []
	for fcode in fpl_codes:
		entry = ffcpicks.find_one({'code': fcode})
		fpl_url = "https://fantasy.premierleague.com/a/team/%d/event/%d" % (fcode, gw)
		player_urls.append(fpl_url)
		if live:
			pts = get_live_points(fcode)
		else:
			pts = entry['points'] - entry['cost']
		points.append(pts)
		transfer_costs.append(entry['cost'])
		scores.append(pts + entry['cost'])
	player_names = get_ffc_players(team_name)
	table_content = list(map(list, zip(player_names, points, transfer_costs, scores, player_urls)))
	table_content = sorted(table_content, key=lambda x: x[1], reverse=True)
	board = []
	for row in table_content:
		item = {
			'Player': row[0],
			'Points': row[1],
			'TC': row[2],
			'Score': row[3],
			'Link': row[4]
		}
		board.append(item)
	return board

def get_scores(team_name, ffc_bench = -1, home_advtg = False, live = True):
	total = 0
	scores = []
	ffcteams = mongo.db.ffcteams
	fpl_codes = ffcteams.find_one({'team': team_name})['codes']
	ffccaptains = mongo.db.ffccaptains
	ffc_captain = ffccaptains.find_one({'team': team_name})['captain']
	if ffc_bench != -1:
		fpl_codes[ffc_bench] = ffc_captain
	else:
		ffcbench = mongo.db.ffcbench
		ffc_bench = ffcbench.find_one({'team': team_name})['bench']
		i = fpl_codes.index(ffc_bench)
		fpl_codes[i] = ffc_captain
	for fcode in fpl_codes:
		scores.append(get_live_points(fcode, live))
	total = sum(scores)
	if home_advtg:
		total += round(0.25*max(scores))
	return int(total)

def get_capatain_scores(team_name):
	teamcapscores = []
	gw = get_current_gw()
	ffcteams = mongo.db.ffcteams
	fpl_codes = ffcteams.find_one({'team': team_name})['codes']
	player_names = get_ffc_players(team_name)
	for name, code in zip(player_names, fpl_codes):
		capscore = []
		for w in range(1, gw + 1):
			gw_url = 'https://fantasy.premierleague.com/drf/event/%d/live' % w
			gw_data = soupify(gw_url)['elements']
			picks_url = 'https://fantasy.premierleague.com/drf/entry/%d/event/%d/picks' % (code, w)
			picks_data = soupify(picks_url)
			for pick in picks_data['picks']:
				if pick['is_vice_captain']:
					capscore.append(int(gw_data[str(pick['element'])]['stats']['total_points']))
		sd = standard_deviation(capscore)
		teamcapscores.append((name, sum(capscore), round(float(sum(capscore)) / float (gw), 2), sd))
	return teamcapscores

def get_team_scores(team_name):
	gkteamscores = {}
	defteamscores = {}
	midteamscores  = {}
	fwdteamscores = {}
	gw = get_current_gw()
	ffcteams = mongo.db.ffcteams
	eplplayers = mongo.db.eplplayers
	eplteams = mongo.db.eplteams
	fpl_codes = ffcteams.find_one({'team': team_name})['codes']
	player_names = get_ffc_players(team_name)
	for name, fcode in zip(player_names, fpl_codes):
		for w in range(11, gw + 1):
			gw_url = 'https://fantasy.premierleague.com/drf/event/%d/live' % w
			gw_data = soupify(gw_url)['elements']
			picks_url = 'https://fantasy.premierleague.com/drf/entry/%d/event/%d/picks' % (fcode, w)
			picks_data = soupify(picks_url)
			for pick in picks_data['picks']:
				player_points = int(gw_data[str(pick['element'])]['stats']['total_points'])
				player_data = eplplayers.find_one({'id': pick['element']})
				if player_data['pos'] == 1:
					if player_data['team'] not in gkteamscores:
						gkteamscores[player_data['team']] = player_points
					else:
						gkteamscores[player_data['team']] += player_points
				elif player_data['pos'] == 2:
					if player_data['team'] not in defteamscores:
						defteamscores[player_data['team']] = player_points
					else:
						defteamscores[player_data['team']] += player_points
				elif player_data['pos'] == 3:
					if player_data['team'] not in midteamscores:
						midteamscores[player_data['team']] = player_points
					else:
						midteamscores[player_data['team']] += player_points
				elif player_data['pos'] == 4:
					if player_data['team'] not in fwdteamscores:
						fwdteamscores[player_data['team']] = player_points
					else:
						fwdteamscores[player_data['team']] += player_points
	gkteamscores = order_dict(dict((eplteams.find_one({'id': k})['short'], v) for k,v in gkteamscores.items()))
	defteamscores = order_dict(dict((eplteams.find_one({'id': k})['short'], v) for k,v in defteamscores.items()))
	midteamscores = order_dict(dict((eplteams.find_one({'id': k})['short'], v) for k,v in midteamscores.items()))
	fwdteamscores = order_dict(dict((eplteams.find_one({'id': k})['short'], v) for k,v in fwdteamscores.items()))
	result = [gkteamscores, defteamscores, midteamscores, fwdteamscores]
	return result

def get_top_chips(rank):
	chips = {}
	chips['w'] = 0
	chips['t'] = 0
	chips['b'] = 0
	chips['a'] = 0
	for i in range(1, 21):
		standings_url = "https://fantasy.premierleague.com/drf/leagues-classic-standings/313?phase=1&le-page=1&ls-page=%d" % (i)
		data = soupify(standings_url)
		entries = data['standings']['results']
		for entry in entries:
			if entry['rank'] > 1000: break
			player_history_url = "https://fantasy.premierleague.com/drf/entry/%d/history" % (entry['entry'])
			history = soupify(player_history_url)
			for chip in history['chips']:
				if chip['chip'] == 2: chips['w'] += 1
				if chip['chip'] == 4: chips['t'] += 1
				if chip['chip'] == 5: chips['b'] += 1
				if chip['chip'] == 3: chips['a'] += 1
	return chips

def get_no_chip_usage():
	ranks = []
	for i in range(1, 21):
		standings_url = "https://fantasy.premierleague.com/drf/leagues-classic-standings/313?phase=1&le-page=1&ls-page=%d" % (i)
		data = soupify(standings_url)
		entries = data['standings']['results']
		for entry in entries:
			player_history_url = "https://fantasy.premierleague.com/drf/entry/%d/history" % (entry['entry'])
			history = soupify(player_history_url)
			if len(history['chips']) <= 1:
				ranks.append(entry['rank'])
	return ranks

def get_chip_usage(team_name):
	team_file = os.path.join(team_folder,team_name)
	team_name, ffc_team = read_in_team(team_file)
	fpl_codes = [entry[1] for entry in list(ffc_team.values())]
	chips = {}
	chips['w'] = 0
	chips['t'] = 0
	chips['b'] = 0
	chips['a'] = 0
	for code in fpl_codes:
		player_history_url = "https://fantasy.premierleague.com/drf/entry/%d/history" % (code)
		history = soupify(player_history_url)
		for chip in history['chips']:
			if chip['chip'] == 1: chips['w'] += 1
			if chip['chip'] == 4: chips['t'] += 1
			if chip['chip'] == 5: chips['b'] += 1
			if chip['chip'] == 3: chips['a'] += 1
	return chips

def get_ffc_hof(gw):
	listScores = []
	eplteams = mongo.db.eplteams
	for team in teamList:
		shortname = eplteams.find_one({'name': team})['short']
		board = team_scoreboard(team, int(gw), live = False)
		for row in board:
			listScores.append((row['Player'], row['Points'], row['Link'], shortname))
	hof = sorted(listScores, key=lambda x:x[1], reverse=True)
	hof = hof[:25]
	board = []
	for item in hof:
		obj = {
			'Player': item[0],
			'Score': item[1],
			'Link': item[2],
			'Team': item[3]
		}
		board.append(obj)
	return board

def update_current_gw():
	static_url = 'https://fantasy.premierleague.com/drf/bootstrap-static'
	static_data = soupify(static_url)
	currentgw = mongo.db.currentgw
	eid = currentgw.find_one()['_id']
	gw = static_data['current-event']
	currentgw.find_one_and_update({'_id': eid}, {'$set': {'gw': gw}})

def update_gw_fixtures():
	gwfixtures = mongo.db.gwfixtures
	gwfixtures.delete_many({})
	gw = mongo.db.currentgw.find_one()['gw']
	live_url = 'https://fantasy.premierleague.com/drf/event/%d/live' % gw
	live_data = soupify(live_url)
	gwfixtures.insert_many({'id': str(fix['id']), 'started': fix['started'], 'home': fix['team_h'], 'away': fix['team_a']} for fix in live_data['fixtures'])

def update_live_points():
	livepoints = mongo.db.livepoints
	livepoints.delete_many({})
	gw = mongo.db.currentgw.find_one()['gw']
	live_url = 'https://fantasy.premierleague.com/drf/event/%d/live' % gw
	live_data = soupify(live_url)['elements']
	livepoints.insert_many({'id': str(player[0]), 'fixture': player[1]['explain'][0][1], 'points': player[1]['stats']['total_points']} for player in live_data.items())
	return 'Live points updated'

def update_ffc_picks():
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

def update_data():
	update_current_gw()
	update_gw_fixtures()
	update_live_points()
	update_ffc_picks()
	return 'Success'