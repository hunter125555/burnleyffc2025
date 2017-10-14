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

def standard_deviation(lst):
	num_items = len(lst)
	mean = sum(lst) / num_items
	differences = [x - mean for x in lst]
	sq_differences = [d ** 2 for d in differences]
	ssd = sum(sq_differences)
	variance = float(ssd) / float(num_items)
	return math.sqrt(variance)

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
			if gwfixtures.find_one({'id': fixid})['started']:
				continue
		current_team.append(eplplayers.find_one({'id': str(pick)})['name'])
		teamcount.append(eplplayers.find_one({'id': str(pick)})['team'])
		if pick == picks['captain'] and include_fpl_captain_twice:
			current_team.append(eplplayers.find_one({'id': str(pick)})['name'])
			if picks['chip'] == "3xc":
				current_team.append(eplplayers.find_one({'id': str(pick)})['name'])
	for pick in picks['bench']:
		if exclude:
			fixid = livepoints.find_one({'id': str(pick)})['fixture']
			if gwfixtures.find_one({'id': fixid})['started']:
				continue
		bench.append(eplplayers.find_one({'id': str(pick)})['name'])
		teamcount.append(eplplayers.find_one({'id': str(pick)})['team'])
	if picks['chip'] == "bboost":
		current_team += bench
	return current_team, bench, teamcount

def get_ffcteamdetails(team_name, ffc_captain = -1, ffc_bench = -1, include_fpl_captain_twice = False, include_fpl_bench=False, exclude = False, team_count = False):
	team_details, team_count_details = [], []
	ffcteams = mongo.db.ffcteams
	eplteams = mongo.db.eplteams
	fpl_codes = ffcteams.find_one({'team': team_name})['codes']
	gw = get_current_gw() 
	if ffc_captain == -1:
		ffccaptains = mongo.db.ffccaptains
		ffc_captain = ffccaptains.find_one({'team': team_name})['captain']
		if ffc_bench != -1:
			fpl_codes[ffc_bench] = ffc_captain
		else:
			ffcbench = mongo.db.ffcbench
			ffc_bench = ffcbench.find_one({'team': team_name})['bench']
			i = fpl_codes.index(ffc_bench)
			fpl_codes[i] = ffc_captain
	else:
		if ffc_bench != -1:
			fpl_codes[ffc_bench] = fpl_codes[ffc_captain]
		else:
			ffcbench = mongo.db.ffcbench
			ffc_bench = ffcbench.find_one({'team': team_name})['bench']
			i = fpl_codes.index(ffc_bench)
			fpl_codes[i] = fpl_codes[ffc_captain]
	for fcode in fpl_codes:
		current, bench, teamcount = get_current_team(fcode, include_fpl_captain_twice, exclude)
		team_details.append(current)
		team_count_details.append(teamcount)
		if include_fpl_bench:
			team_details.append(bench)
	team_details = flatten(team_details)
	total_player_count = dict(Counter(team_details))
	total_player_count_sorted = order_dict(total_player_count)
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
		import code; code.interact(local=locals())
		return final_dict
	else:
		return total_player_count_sorted

def get_differentials(t1,t2):
	players_both_sides = set(list(t1.keys()) + list(t2.keys()))
	diff = {key: t1.get(key, 0) - t2.get(key, 0) for key in players_both_sides}
	diff_sorted = order_dict(diff)
	return diff_sorted

def get_live_points(entry_code):
	gw_score = 0
	ffcpicks = mongo.db.ffcpicks
	livepoints = mongo.db.livepoints
	picks = ffcpicks.find_one({'code': entry_code})
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

def team_scoreboard(team_name, gw = -1):
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
		points.append(entry['points'])
		transfer_costs.append(entry['cost'])
		scores.append(entry['points'] - entry['cost'])
	player_names = get_ffc_players(team_name)
	table_content = list(map(list, zip(player_names, points, transfer_costs, scores, player_urls)))
	table_content = sorted(table_content, key=lambda x: x[3], reverse=True)
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

def get_scores(team_name, ffc_captain = -1, ffc_bench = -1, home_advtg = False):
	total = 0
	scores = []
	ffcteams = mongo.db.ffcteams
	fpl_codes = ffcteams.find_one({'team': team_name})['codes']
	if ffc_captain == -1:
		ffccaptains = mongo.db.ffccaptains
		ffc_captain = ffccaptains.find_one({'team': team_name})['captain']
		if ffc_bench != -1:
			fpl_codes[ffc_bench] = ffc_captain
		else:
			ffcbench = mongo.db.ffcbench
			ffc_bench = ffcbench.find_one({'team': team_name})['bench']
			i = fpl_codes.index(ffc_bench)
			fpl_codes[i] = ffc_captain
	else:
		if ffc_bench != -1:
			fpl_codes[ffc_bench] = fpl_codes[ffc_captain]
		else:
			ffcbench = mongo.db.ffcbench
			ffc_bench = ffcbench.find_one({'team': team_name})['bench']
			i = fpl_codes.index(ffc_bench)
			fpl_codes[i] = fpl_codes[ffc_captain]
	for fcode in fpl_codes:
		scores.append(get_live_points(fcode))
	total = sum(scores)
	if home_advtg:
		total += math.floor(0.25*max(scores))
	return int(total)

def get_capatain_scores(filename):
	teamcapscores = []
	gw = get_current_gw()
	team_file = os.path.join(team_folder,filename)
	team_name, ffc_team = read_in_team(team_file)
	fpl_codes = [entry[1] for entry in list(ffc_team.values())]
	player_names = [entry[0] for entry in list(ffc_team.values())]
	for name, code in zip(player_names, fpl_codes):
		capscore = []
		for w in range(1, gw + 1):
			entry_url = "https://fantasy.premierleague.com/drf/entry/%d/event/%d" % (code, w)
			data = soupify(entry_url)
			for pick in data['picks']:
				if pick['is_captain']:
					capscore.append(int(pick['points']) * int(pick['multiplier']))
		sd = standard_deviation(capscore)
		teamcapscores.append((name, sum(capscore), float(sum(capscore)) / float (gw), sd))
	return teamcapscores

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
	for team in teamList:
		board = team_scoreboard(team, int(gw))
		for row in board:
			listScores.append((row['Player'], row['Score'], row['Link'], team))
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