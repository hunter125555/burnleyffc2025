'use strict';

angular.module('AngularFlask', ['angularFlaskServices', 'smart-table'])
	.run(function($rootScope) {
    	$rootScope.teamList = ['Arsenal', 'Brighton', 'Bournemouth', 'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Huddersfield', 'Leicester', 'Liverpool', 'Man City',  'Man Utd', 'Newcastle', 'Southampton', 'Stoke', 'Swansea', 'Spurs', 'Watford', 'West Brom', 'West Ham'];
	})
	.config(['$routeProvider', '$locationProvider',
		function($routeProvider, $locationProvider) {
		$routeProvider
		.when('/', {
			templateUrl: '../static/partials/landing.html',
			controller: IndexController
		})
		.when('/tie', {
			templateUrl: '../static/partials/tie.html',
			controller: TieController
		})
		.when('/post', {
			templateUrl: '../static/partials/post-list.html',
			controller: PostListController
		})
		.when('/scorecard', {
			templateUrl: '../static/partials/scoreboard.html',
			controller: ScoreBoardController
		})
		.when('/diff', {
			templateUrl: '../static/partials/diff.html',
			controller: DiffController
		})
		.when('/player-count', {
			templateUrl: '../static/partials/count.html',
			controller: PlayerCountController
		})
		.when('/halloffame', {
			templateUrl: '../static/partials/hall.html',
			controller: HallController
		})
		.when('/livefixtures', {
			templateUrl: '../static/partials/fixtures.html',
			controller: FixController
		})
		.otherwise({
			redirectTo: '/'
		});
		$locationProvider.html5Mode(true);
	}])
;

