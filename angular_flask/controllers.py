import os
import helper

from flask import Flask, request, Response, json
from flask import render_template, url_for, redirect, send_from_directory, jsonify
from flask import send_file, make_response, abort

from angular_flask import app

# routing for API endpoints, generated from the models designated as API_MODELS
from angular_flask.core import api_manager
from angular_flask.models import *

for model_name in app.config['API_MODELS']:
	model_class = app.config['API_MODELS'][model_name]
	api_manager.create_api(model_class, methods=['GET', 'POST'])

session = api_manager.session


# routing for basic pages (pass routing onto the Angular app)
@app.route('/player_names', methods = ['GET'])
def get_player_names():
	team_name = request.args.get('team') + ".txt"
	team_name = team_name.lower()
	return json.dumps(helper.get_ffc_players(team_name))

@app.route('/scoreboard', methods = ['GET'])
def get_scorecard():
	team_name = request.args.get('team') + ".txt"
	team_name = team_name.lower()
	return json.dumps(helper.team_scoreboard(team_name))

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
	teamA = request.args.get('teamA') + ".txt"
	teamB = request.args.get('teamB') + ".txt"
	captainA = request.args.get('captainA')
	captainB = request.args.get('captainB')
	benchA = request.args.get('benchA')
	benchB = request.args.get('benchB')
	ffc_captainA = int(captainA) if captainA != 'null' else -1
	ffc_benchA = int(benchA) if benchA != 'null' else -1
	ffc_captainB = int(captainB) if captainB != 'null' else -1
	ffc_benchB = int(benchB) if benchB != 'null' else -1
	teamA_counts = helper.get_ffcteamdetails(teamA.lower(), ffc_captain = ffc_captainA, ffc_bench = ffc_benchA, include_fpl_captain_twice = captain, include_fpl_bench=bench, exclude = exclude)
	teamB_counts = helper.get_ffcteamdetails(teamB.lower(), ffc_captain = ffc_captainB, ffc_bench = ffc_benchB, include_fpl_captain_twice = captain, include_fpl_bench=bench, exclude = exclude)
	return json.dumps(helper.get_differentials(teamA_counts, teamB_counts).items(), sort_keys = False)

@app.route('/count', methods = ['GET'])
def get_player_count():
	team_name = request.args.get('team') + ".txt"
	team_name = team_name.lower()
	return json.dumps(helper.get_ffcteamdetails(team_name, include_fpl_bench = True, team_count = True).items(), sort_keys= False)

@app.route('/tie_details', methods = ['GET'])
def get_tie_scorecards():
	teamA = request.args.get('teamA') + ".txt"
	teamB = request.args.get('teamB') + ".txt"
	captainA = request.args.get('captainA')
	captainB = request.args.get('captainB')
	benchA = request.args.get('benchA')
	benchB = request.args.get('benchB')
	teamA_card = helper.team_scoreboard(teamA.lower())
	teamB_card = helper.team_scoreboard(teamB.lower())
	ffc_captainA = int(captainA) if captainA != 'null' else -1
	ffc_benchA = int(benchA) if benchA != 'null' else -1
	ffc_captainB = int(captainB) if captainB != 'null' else -1
	ffc_benchB = int(benchB) if benchB != 'null' else -1
	teamA_score = helper.get_scores(teamA.lower(), ffc_captain = ffc_captainA, ffc_bench = ffc_benchA, home_advtg = True)
	teamB_score = helper.get_scores(teamB.lower(), ffc_captain = ffc_captainB, ffc_bench = ffc_benchB, home_advtg = False)
	scores = []
	scores.append(teamA_card)
	scores.append(teamB_card)
	scores.append(teamA_score)
	scores.append(teamB_score)
	return json.dumps(scores)

@app.route('/')
@app.route('/tie')
@app.route('/blog')
@app.route('/scorecard')
@app.route('/diff')
@app.route('/player-count')
@app.route('/halloffame')
def basic_pages(**kwargs):
	return make_response(open('angular_flask/templates/index.html').read())


# routing for CRUD-style endpoints
# passes routing onto the angular frontend if the requested resource exists
from sqlalchemy.sql import exists

crud_url_models = app.config['CRUD_URL_MODELS']


@app.route('/<model_name>/')
@app.route('/<model_name>/<item_id>')
def rest_pages(model_name, item_id=None):
	if model_name in crud_url_models:
		model_class = crud_url_models[model_name]
		if item_id is None or session.query(exists().where(
				model_class.id == item_id)).scalar():
			return make_response(open(
				'angular_flask/templates/index.html').read())
	abort(404)


# special file handlers and error handlers
@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'),
							   'img/favicon.ico')


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404
