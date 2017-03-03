
'use strict';

/* Controllers */

function IndexController($scope, $rootScope) {
	
}

function AboutController($scope) {
	
}

function ScoreBoardController($scope, $http) {
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

function DiffController($scope, $rootScope, $http) {
	$scope.diff = [];
	$scope.teamA = null;
	$scope.teamB = null;
	$scope.bench = "no";
	$scope.teamList = $rootScope.teamList;
	$scope.loadDiff = function() {
		$http.get("/differentials?teamA=" + $scope.teamA + "&teamB=" + $scope.teamB + "&bench=" + $scope.bench).
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
	$scope.teamA = "Arsenal";
	$scope.teamB = "Burnley"
	$scope.loadBoard = function() {
		$http.get("/tie_details?teamA=" + $scope.teamA + "&teamB=" + $scope.teamB).
			then(function(response) {
				$scope.displayTable = true;
				$scope.boardA = response.data[0];
				$scope.boardB = response.data[1];
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