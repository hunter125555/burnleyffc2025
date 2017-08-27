
'use strict';

/* Controllers */

function IndexController($scope, $rootScope) {
	
}

function AboutController($scope) {
	
}

function ScoreBoardController($scope, $rootScope, $http) {
	$scope.board = [];
	$scope.displayTable = false;
	$scope.team = "Arsenal";
	$scope.loadBoard = function() {
		$http.get("/scoreboard?team=" + $scope.team).
			then(function(response) {
				$scope.displayTable = true;
				$scope.board = response.data;
				console.log(response.data);
		}, function(error) {
			console.log(error);
		});
	}
}

function HallController($scope, $rootScope, $http) {
	$scope.board = [];
	$scope.displayTable = false;
	$scope.gw = "";
	$scope.loadHof= function() {
		$http.get("/hof?gw=" + $scope.gw).
			then(function(response) {
				$scope.displayTable = true;
				$scope.board = response.data;
				for(var i = 0; i < 15; i++) {
					console.log($scope.board[i].Player + " (" + $scope.board[i].Team + "): " + $scope.board[i].Score);
				}
				console.log(response.data);
		}, function(error) {
			console.log(error);
		});
	}
}

function DiffController($scope, $rootScope, $http) {
	$scope.diff = [];
	$scope.teamA = null;
	$scope.teamB = null;
	$scope.fplBench = "no";
	$scope.fplCaptain = "no";
	$scope.excludeHasPlayed = "no";
	$scope.displaySub = false;
	$scope.homeTeam = [];
	$scope.awayTeam = [];
	$scope.captainA = null;
	$scope.captainB = null;
	$scope.benchA = null;
	$scope.benchB = null;
	$scope.loadPlayers = function() {
		if ($scope.teamA === $scope.teamB) {
			alert("Two teams cannot be the same");
		} else {
			$scope.displaySub = true;
			$http.get("/player_names?team=" + $scope.teamA).
				then(function(response) {
					$scope.homeTeam = response.data;
					console.log(response.data);
			}, function(error) {
				console.log(error);
			});
			$http.get("/player_names?team=" + $scope.teamB).
				then(function(response) {
					$scope.awayTeam = response.data;
					console.log(response.data);
			}, function(error) {
				console.log(error);
			});
		}
	}
	$scope.loadDiff = function() {
		$http.get("/differentials?teamA=" + $scope.teamA + "&teamB=" + $scope.teamB + "&bench=" + $scope.fplBench + "&captain=" + $scope.fplCaptain + "&exclude=" + $scope.excludeHasPlayed +"&captainA=" + $scope.captainA + "&captainB=" + $scope.captainB  + "&benchA=" + $scope.benchA + "&benchB=" + $scope.benchB).
			then(function(response) {
				$scope.diff = response.data;
				console.log(response.data);
		}, function(error) {
			console.log(error);
		});
	}
}

function PlayerCountController($scope, $rootScope, $http) {
	$scope.counts = [];
	$scope.team = null;
	$scope.loadCounts = function() {
		$http.get("/count?team=" + $scope.team).
			then(function(response) {
				$scope.counts = response.data;
				console.log(response.data);
		}, function(error) {
			console.log(error);
		});
	}
}

function TieController($scope, $rootScope, $http) {
	$scope.boardA = [];
	$scope.boardB = [];
	$scope.displayTable = false;
	$scope.displaySub = false;
	$scope.teamA = "Arsenal";
	$scope.teamB = "Burnley";
	$scope.captainA = null;
	$scope.captainB = null;
	$scope.benchA = null;
	$scope.benchB = null;
	$scope.homeTeam = [];
	$scope.awayTeam = [];
	$scope.homeScore = null;
	$scope.awayScore = null;
	$scope.loadPlayers = function() {
		if ($scope.teamA === $scope.teamB) {
			alert("Two teams cannot be the same");
		} else {
			$scope.displaySub = true;
			$http.get("/player_names?team=" + $scope.teamA).
				then(function(response) {
					$scope.homeTeam = response.data;
					console.log(response.data);
			}, function(error) {
				console.log(error);
			});
			$http.get("/player_names?team=" + $scope.teamB).
				then(function(response) {
					$scope.awayTeam = response.data;
					console.log(response.data);
			}, function(error) {
				console.log(error);
			});
		}
	}
	$scope.loadBoard = function() {
		$http.get("/tie_details?teamA=" + $scope.teamA + "&teamB=" + $scope.teamB + "&captainA=" + $scope.captainA + "&captainB=" + $scope.captainB  + "&benchA=" + $scope.benchA + "&benchB=" + $scope.benchB).
			then(function(response) {
				$scope.displayTable = true;
				$scope.boardA = response.data[0];
				$scope.boardB = response.data[1];
				$scope.homeScore = response.data[2];
				$scope.awayScore = response.data[3];
				console.log(response.data);
		}, function(error) {
			console.log(error);
		});
	}
}

function PostListController($scope, Post) {
	var postsQuery = Post.get({}, function(posts) {
		$scope.posts = posts.objects;
	});
}

function PostDetailController($scope, $routeParams, Post) {
	var postQuery = Post.get({ postId: $routeParams.postId }, function(post) {
		$scope.post = post;
	});
}