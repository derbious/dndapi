var dndApp = angular.module('dnd',[]);

dndApp.controller('LoginController', ['$scope', '$http', function($scope, $http) {
    $scope.apikey = "";
    $scope.doLogin = function(user){
        console.log('Doing Login AJAX shit');
        $http({
            method: 'POST',
            url: 'api/auth',
            headers: {
                'Content-Type': 'application/json'
            },
            data: user
        }).then(function successCallback(response) {
            console.log('Success /api/auth');
            $scope.apikey = response;
        }, function errorCallback(response) {
            $scope.apikey="ERROR";
        });
    }
}]);