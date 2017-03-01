
'use strict';

/* Controllers */

function IndexController($scope, $http) {

}

function AboutController($scope) {
	
}

function ScoreBoardController($scope, $http) {
	$scope.board = [];
	$scope.team = "arsenal";
	$scope.loadBoard = function() {
		$http.get("/scoreboard?team=" + $scope.team).
			then(function(response) {
				$scope.board = response.data;
				console.log(response.data);
		}, function(error) {
			console.log(error);
		});
	}
}

function DiffController($scope, $http) {
	$scope.diff = [];
	$scope.teamA = "burnley";
	$scope.teamB = "liverpool";
	$scope.bench = "no";
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

function PlayerCountController($scope, $http) {
	$scope.counts = [];
	$scope.team = "burnley";
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

function TieController($scope) {

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