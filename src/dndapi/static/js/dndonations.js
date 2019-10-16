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

// The Search Controller handles the donor search.
dndApp.controller('SearchController', ['$rootScope', '$scope', '$http', function($rootScope, $scope, $http) {
    $scope.donor_results = [];
    $scope.display = false;

    // Start displaying after login
    $rootScope.$on('login_successful', function(){
        $scope.display = true;
    });

    $scope.performSearch = function(query){
        var token = sessionStorage.getItem('access_token');
        console.log('Looking up donors');
        $http({
            method: 'GET',
            url: "api/search?q="+query,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            }
        }).then(function successCallback(response) {
            console.log('Success /api/search');
            $scope.donor_results = response.data;
            $scope.display = true;
        }, function errorCallback(response) {
            $scope.display = false;
        });
    }

    //Signal that we should show this donor info
    $scope.showDonor = function(donor_id){
        console.log('in showDonor()');
        console.log(donor_id);
        $rootScope.$emit('show_donor', {"id": donor_id});
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


// The Donor controller.
dndApp.controller('DonorController', ['$rootScope', '$scope', '$http', function($rootScope, $scope, $http) {
    $scope.display = false;
    $scope.nd_display = false;
    $scope.error_msg = "";
    $scope.nd_error_msg = "";
    $scope.donor = {}
    $scope.donation = {}

    $rootScope.$on('login_successful', function(){
        $scope.display = true;
    });  

    // Given the current donor.id, refresh the information
    $scope.refreshDonorInfo = function(){
        var token = sessionStorage.getItem('access_token');
        $http({
            method: 'GET',
            url: "api/donors/"+$scope.donor.id,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            }
        }).then(function successCallback(response) {
            console.log('Successful call to /api/donors [GET]');
            $scope.donor = response.data;
        }, function errorCallback(response) {
            $scope.error_msg = "Could not get donor";
        });
    }


    $rootScope.$on('show_donor', function(e, d){
        $scope.donor.id = d.id;
        $scope.refreshDonorInfo();
    });

    $scope.showDonationForm = function(){
        $scope.nd_display = true;
        $scope.donation = {};
    };

    $scope.addDonation = function(){
        var token = sessionStorage.getItem('access_token');
        console.log('Adding a donation');
        
        // Create the dontaion object
        var d = {
            "donor_id": $scope.donor.id,
            "amount": $scope.donation.amount,
            "method": $scope.donation.method
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
            $scope.nd_display = false; // Hide the donation modal
            //Refresh the donor Gold count
            $scope.refreshDonorInfo();
        }, function errorCallback(response) {
            $scope.nd_error_msg = "Could not post donation";
        });
    };

}]);