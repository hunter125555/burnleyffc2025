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

@app.route('/scoreboard', methods = ['GET'])
def get_scorecard():
	team_name = request.args.get('team') + ".txt"
	team_name = team_name.lower()
	return json.dumps(helper.team_scoreboard(team_name))

@app.route('/differentials', methods = ['GET'])
def get_differentials():
	if request.args.get('bench') == "yes": bench = True
	else: bench = False 
	teamA = request.args.get('teamA') + ".txt"
	teamB = request.args.get('teamB') + ".txt"
	if teamA != teamB:
		teamA_counts = helper.get_ffcteamdetails(teamA.lower(), include_fpl_bench=bench)
		teamB_counts = helper.get_ffcteamdetails(teamB.lower(), include_fpl_bench=bench)
		return json.dumps(helper.get_differentials(teamA_counts, teamB_counts).items(), sort_keys = False)
	else:
		return None

@app.route('/count', methods = ['GET'])
def get_player_count():
	team_name = request.args.get('team') + ".txt"
	team_name = team_name.lower()
	return json.dumps(helper.get_ffcteamdetails(team_name).items(), sort_keys= False)

@app.route('/tie_details', methods = ['GET'])
def get_tie_scorecards():
	teamA = request.args.get('teamA') + ".txt"
	teamB = request.args.get('teamB') + ".txt"
	if teamA != teamB:
		teamA_card = helper.team_scoreboard(teamA.lower())
		teamB_card = helper.team_scoreboard(teamB.lower())
		scores = []
		scores.append(teamA_card, teamB_card)
		return jsonify(scores)
	else:
		return None

@app.route('/')
@app.route('/tie')
@app.route('/blog')
@app.route('/scorecard')
@app.route('/diff')
@app.route('/player-count')
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
