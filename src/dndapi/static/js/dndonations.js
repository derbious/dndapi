// Clear out any previous session keys
sessionStorage.clear();

var dndApp = angular.module('dnd',[]);

// The LoginController handles the login json all
dndApp.controller('LoginController', ['$rootScope', '$scope', '$http', function($rootScope, $scope, $http) { 
    $scope.apitoken = "";
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
            $scope.apitoken = response.data.access_token;
            sessionStorage.setItem('access_token', response.data.access_token);
            //Tell everyone to show up
            $rootScope.$emit("login_successful", {});
        }, function errorCallback(response) {
            $scope.apitoken="ERROR";
        });
    }
}]);


// View Donor Controller
dndApp.controller('ViewDonorController', ['$scope', '$http', function($scope, $http) {
    $scope.donors = [];
    $scope.current_donor = null;
    $scope.panel = "";
    $scope.nd = {'method': 'cash'};
    $scope.character = {};

    $scope.refreshDonors = function(){
        var token = sessionStorage.getItem('access_token');
        console.log('Refreshing all donor stuff');
        $http({
            method: 'GET',
            url: "api/donors",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            }
        }).then(function successCallback(response) {
            $scope.donors = response.data;
        });
    }

    // Set the current donor to the one with the correct donor id
    $scope.showDonor = function(did){
        $scope.current_donor = $scope.donors.find(function(d){
            return d.id === did;
        });
    }

    // Given the current donor.id, refresh the information
    $scope.refreshCurrentDonor = function(){
        var token = sessionStorage.getItem('access_token');
        $http({
            method: 'GET',
            url: "api/donors/"+$scope.current_donor.id,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            }
        }).then(function successCallback(response) {
            console.log('Successful call to /api/donors [GET]');
            $scope.current_donor = response.data;
        }, function errorCallback(response) {
            $scope.error_msg = "Could not get donor";
        });
    };

    $scope.addDonation = function(){
        var token = sessionStorage.getItem('access_token');
        console.log('Adding a donation');
        
        // Create the dontaion object
        var d = {
            "donor_id": $scope.current_donor.id,
            "amount": $scope.nd.amount,
            "method": $scope.nd.method
        }
        $http({
            method: 'POST',
            url: "api/donations/",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            },
            data: d
        }).then(function successCallback(response) {
            console.log('Successful call to /api/donations [POST]');
            //Refresh the donor Gold count
            $scope.refreshCurrentDonor();
        }, function errorCallback(response) {
            $scope.nd_error_msg = "Could not post donation";
        });
    };

    $scope.createCharacter = function() {
        console.log('Creating character stub');
        var token = sessionStorage.getItem('access_token');
        
        // Create the character obj
        var d = {
            "player_id": $scope.current_donor.id,
            "name": $scope.character.name,
            "race": $scope.character.race,
            "char_class": $scope.character.char_class
        }
        $http({
            method: 'POST',
            url: "api/characters/",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            },
            data: d
        }).then(function successCallback(response) {
            console.log('Successful call to /api/characters [POST]');
            $scope.refreshCurrentDonor();
        }, function errorCallback(response) {
            $scope.nd_error_msg = "Could not post donation";
        });
    };
}]);


// The Add Donor controller.
dndApp.controller('NewDonorController', ['$rootScope', '$scope', '$http', function($rootScope, $scope, $http) {
    $scope.display = false;

    $rootScope.$on('login_successful', function(){
        $scope.display = true;
    });

    $scope.addDonor = function(){
        var token = sessionStorage.getItem('access_token');
        console.log("Token is: "+token)
        $scope.error_msg = "";
        console.log('Inserting new donor');
        $http({
            method: 'POST',
            url: "api/donors",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            },
            data: $scope.donor
        }).then(function successCallback(response) {
            console.log('Successful call to /api/donors [POST]');
            $scope.donor = {};
        }, function errorCallback(response) {
            $scope.error_msg = "Could not insert donor";
        });
    }
}]);


