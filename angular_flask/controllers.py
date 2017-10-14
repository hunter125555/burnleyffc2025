import os
import helper

from flask import Flask, request, Response, json
from flask import render_template, url_for, redirect, send_from_directory, jsonify
from flask import send_file, make_response, abort

from angular_flask import app
from angular_flask.core import mongo

# routing for basic pages (pass routing onto the Angular app)
@app.route('/player_names', methods = ['GET'])
def get_player_names():
	return json.dumps(helper.get_ffc_players(request.args.get('team')))

@app.route('/scoreboard', methods = ['GET'])
def get_scorecard():
	return json.dumps(helper.team_scoreboard(request.args.get('team')))

@app.route('/captain_scores', methods = ['GET'])
def get_captain_scores():
	team_name = request.args.get('team') + ".txt"
	team_name = team_name.lower()
	return json.dumps(helper.get_capatain_scores(team_name))

@app.route('/chip_usage', methods = ['GET'])
def get_chips_usage():
	team_name = request.args.get('team') + ".txt"
	team_name = team_name.lower()
	return json.dumps(helper.get_chip_usage(team_name.lower()))

@app.route('/topchips', methods = ['GET'])
def get_chips():
	return json.dumps(helper.get_top_chips(1000).items())

@app.route('/nochips', methods = ['GET'])
def get_no_chips():
	return json.dumps(helper.get_no_chip_usage())

@app.route('/hof', methods = ['GET'])
def get_ffc_hof():
	gw = request.args.get('gw')
	return json.dumps(helper.get_ffc_hof(gw))

@app.route('/differentials', methods = ['GET'])
def get_differentials():
	bench = True if request.args.get('bench') == "yes" else False
	captain = True if request.args.get('captain') == "yes" else False
	exclude = True if request.args.get('exclude') == "yes" else False
	teamA = request.args.get('teamA')
	teamB = request.args.get('teamB')
	captainA = request.args.get('captainA')
	captainB = request.args.get('captainB')
	benchA = request.args.get('benchA')
	benchB = request.args.get('benchB')
	ffc_captainA = int(captainA) if captainA != 'null' else -1
	ffc_benchA = int(benchA) if benchA != 'null' else -1
	ffc_captainB = int(captainB) if captainB != 'null' else -1
	ffc_benchB = int(benchB) if benchB != 'null' else -1
	teamA_counts = helper.get_ffcteamdetails(teamA, ffc_captain = ffc_captainA, ffc_bench = ffc_benchA, include_fpl_captain_twice = captain, include_fpl_bench=bench, exclude = exclude)
	teamB_counts = helper.get_ffcteamdetails(teamB, ffc_captain = ffc_captainB, ffc_bench = ffc_benchB, include_fpl_captain_twice = captain, include_fpl_bench=bench, exclude = exclude)
	return json.dumps(helper.get_differentials(teamA_counts, teamB_counts).items(), sort_keys = False)

@app.route('/count', methods = ['GET'])
def get_player_count():
	team_name = request.args.get('team')
	return json.dumps(helper.get_ffcteamdetails(team_name, include_fpl_bench = True, team_count = True).items(), sort_keys= False)

@app.route('/tie_details', methods = ['GET'])
def get_tie_scorecards():
	teamA = request.args.get('teamA')
	teamB = request.args.get('teamB')
	captainA = request.args.get('captainA')
	captainB = request.args.get('captainB')
	benchA = request.args.get('benchA')
	benchB = request.args.get('benchB')
	teamA_card = helper.team_scoreboard(teamA)
	teamB_card = helper.team_scoreboard(teamB)
	ffc_captainA = int(captainA) if captainA != 'null' else -1
	ffc_benchA = int(benchA) if benchA != 'null' else -1
	ffc_captainB = int(captainB) if captainB != 'null' else -1
	ffc_benchB = int(benchB) if benchB != 'null' else -1
	teamA_score = helper.get_scores(teamA, ffc_captain = ffc_captainA, ffc_bench = ffc_benchA, home_advtg = True)
	teamB_score = helper.get_scores(teamB, ffc_captain = ffc_captainB, ffc_bench = ffc_benchB, home_advtg = False)
	scores = []
	scores.append(teamA_card)
	scores.append(teamB_card)
	scores.append(teamA_score)
	scores.append(teamB_score)
	return json.dumps(scores)

@app.route('/fixtures')
def get_all_fixtures_score():
	livefixtures = []
	gwfixtures = mongo.db.gwfixtures
	eplteams = mongo.db.eplteams
	fixtures = gwfixtures.find({})
	for fix in fixtures:
		home = fix['home']
		away = fix['away']
		started = fix['started']
		homeTeam = eplteams.find_one({'id': home})['name']
		awayTeam = eplteams.find_one({'id': away})['name']
		homeTeamScore = helper.get_scores(homeTeam, ffc_captain = -1, ffc_bench = -1, home_advtg = True)
		awayTeamScore = helper.get_scores(awayTeam, ffc_captain = -1, ffc_bench = -1, home_advtg = False)
		livefixtures.append([(homeTeam, homeTeamScore), (awayTeam, awayTeamScore)])
	return json.dumps(livefixtures)

@app.route('/')
@app.route('/tie')
@app.route('/scorecard')
@app.route('/diff')
@app.route('/player-count')
@app.route('/halloffame')
@app.route('/livefixtures')
def basic_pages(**kwargs):
	return make_response(open('angular_flask/templates/index.html').read())

# special file handlers and error handlers
@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'),
							   'img/favicon.ico')


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404