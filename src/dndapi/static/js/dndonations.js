// Clear out any previous session keys
sessionStorage.clear();

var dndApp = angular.module('dnd',[]);

// The LoginController handles the login json all
dndApp.controller('LoginController', ['$rootScope', '$scope', '$http', function($rootScope, $scope, $http) { 
    $scope.apitoken = "";
    $scope.show_modal = false;
    $scope.login_successful = false;

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
            $scope.show_modal = false;
            $scope.login_successful = true;
        }, function errorCallback(response) {
            $scope.apitoken="ERROR";
        });
    }
}]);


// View Donor Controller
dndApp.controller('ViewDonorController', ['$scope', '$http', function($scope, $http) {
    $scope.donors = [];
    $scope.current_donor = null;
    $scope.current_donor_characters = null;
    $scope.panel = "";
    $scope.nd = {'method': 'cash'};
    $scope.character = {};
    $scope.baneamt = "5";
    $scope.boonamt = "5";

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
        $scope.panel = "none";
        $scope.current_donor = $scope.donors.find(function(d){
            return d.id === did;
        });
        $scope.refreshCurrentDonor();
    };

    // Given the current donor.id, refresh the information
    $scope.refreshCurrentDonor = function(){
        var token = sessionStorage.getItem('access_token');
        // Pull the Donor information
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
        // Also pull their registered characters
        $http({
            method: 'GET',
            url: "api/characters/forplayer/"+$scope.current_donor.id,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            }
        }).then(function successCallback(response) {
            console.log('Successful call to /api/characters/forplayer [GET]');
            $scope.current_donor_characters = response.data;
        }, function errorCallback(response) {
            $scope.error_msg = "Could not get donors characters";
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
            $scope.refreshDonors();
            $scope.$apply();
        }, function errorCallback(response) {
            $scope.error_msg = "Could not post donation";
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
            "char_class": $scope.character.char_class,
            "benefactor_id": Number($scope.character.benefactor)
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
            $scope.refreshDonors();
            $scope.refreshCurrentDonor();
        }, function errorCallback(response) {
            $scope.error_msg = "Could not register character";
        });
    };

    $scope.addPurchase = function(reason){
        var token = sessionStorage.getItem('access_token');
        if(reason == 'boon'){
            amt = new Number(this.boonamt);
        }else{
            amt = new Number(this.baneamt);
        }
        // See if current_donor can afford it.
        if($scope.current_donor.available_gold < amt){
            $scope.error_msg = "not enough gold to purchase";
            return;
        }
        // Create the purchase object
        var p = {
            "donor_id": $scope.current_donor.id,
            "reason": reason,
            "amount": amt
        }
        this.boonamt = "5";
        this.baneamt = "5";

        $http({
            method: 'POST',
            url: "api/purchases/",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            },
            data: p
        }).then(function successCallback(response) {
            console.log('Successful call to /api/purchases [POST]');
            $scope.refreshDonors();
            $scope.refreshCurrentDonor();
            $scope.$apply();
            // Reset the donation radio buttons
        }, function errorCallback(response) {
            $scope.error_msg = "Could not post purchase";
        });
    };


    // remove a character from the queue
    $scope.removeFromQueue = function(cid){
        var token = sessionStorage.getItem('access_token');
        $http({
            method: 'POST',
            url: "api/queue/remove/"+cid,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            }
        }).then(function successCallback(response) {
            console.log('Successful call to /api/queue/remove/<id> [POST]');
            $scope.refreshCurrentDonor();
        }, function errorCallback(response) {
            $scope.error_msg = "Error removing char from queue";
        });
    };

    // remove a character from the queue
    $scope.unremoveFromQueue = function(cid){
        var token = sessionStorage.getItem('access_token');
        $http({
            method: 'POST',
            url: "api/queue/unremove/"+cid,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            }
        }).then(function successCallback(response) {
            console.log('Successful call to /api/queue/unremove/<id> [POST]');
            $scope.refreshCurrentDonor();
        }, function errorCallback(response) {
            $scope.error_msg = "Error adding char back to queue";
        });
    };
}]);


// The Add Donor controller.
dndApp.controller('NewDonorController', ['$rootScope', '$scope', '$http', function($rootScope, $scope, $http) {
    $scope.disabled = true;

    $rootScope.$on('login_successful', function(){
        $scope.disabled = false;
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


// The Stream controller
dndApp.controller('StreamController', ['$scope', '$http', '$interval', function($scope, $http, $interval) {
    $scope.error_msg = "";
    $scope.newdm = {
        "name": "",
        "team": "moonwatch"
    };
    $scope.current_dm = {};
    $scope.nextgoal = "$750";

    $scope.regNewDm = function(){
        var token = sessionStorage.getItem('access_token');
        console.log('Registering New DM');
        dm = {
            "name": $scope.newdm.name,
            "team": $scope.newdm.team
        }
        $http({
            method: 'POST',
            url: "api/dms",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            },
            data: dm
        }).then(function successCallback(response) {
            console.log('Successful call to /api/dms [POST]');
            $scope.current_dm = response.data
            $scope.refreshStreaminfo();
        }, function errorCallback(response) {
            $scope.error_msg = "Could not insert DM";
        });
    };

    $scope.setTicker = function(){
        var token = sessionStorage.getItem('access_token');
        console.log('changing out the ticker');
        tk = {
            "key": "ticker",
            "value": $scope.stream_ticker
        }
        $http({
            method: 'POST',
            url: "api/meta",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            },
            data: tk
        }).then(function successCallback(response) {
            console.log('Successful call to /api/meta [POST]');
            $scope.refreshStreaminfo();
        }, function errorCallback(response) {
            $scope.error_msg = "Could not insert the new ticker";
        });
    };

    $scope.setNextgoal = function(){
        var token = sessionStorage.getItem('access_token');
        console.log("in setNextgoal", $scope.nextgoal);
        goal = {
            "key": "nextgoal",
            "value": $scope.nextgoal
        }
        $http({
            method: 'POST',
            url: "api/meta",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            },
            data: goal
        }).then(function successCallback(response) {
            console.log('Successful call to /api/meta [POST] (GOAL)');
            $scope.refreshStreaminfo();
        }, function errorCallback(response) {
            $scope.error_msg = "Could not insert the next goal";
        });
    };

    // Interval to pull the currentDM and meta info
    $scope.refreshStreaminfo = function(){
        var token = sessionStorage.getItem('access_token');
        $http({
            method: 'GET',
            url: "api/currentdm",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            }
        }).then(function successCallback(response) {
            console.log('Successful call to /api/currentdm [GET]');
            $scope.current_dm = response.data;
        }, function errorCallback(response) {
            $scope.queue_error = "Could not fetch queue";
        });

        $http({
            method: 'GET',
            url: "api/meta/ticker",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            }
        }).then(function successCallback(response) {
            console.log('Successful call to /api/meta/ticker [GET]');
            $scope.current_stream_msg = response.data.value;
        }, function errorCallback(response) {
            $scope.queue_error = "Could not fetch ticker";
        });

        $http({
            method: 'GET',
            url: "api/meta/nextgoal",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            }
        }).then(function successCallback(response) {
            console.log('Successful call to /api/meta/nextgoal [GET]');
            $scope.current_nextgoal = response.data.value;
        }, function errorCallback(response) {
            $scope.queue_error = "Could not fetch goal";
        });
    };
    $interval($scope.refreshStreaminfo, 10000); //10s interval

}]);

// the Queue controller
dndApp.controller('QueueController', ['$scope', '$http', '$interval', function($scope, $http, $interval) {
    //Pull in the math controller. this is for Math.pow()
    $scope.Number = window.Number;
    $scope.Math = window.Math;

    $scope.queue_error = "";
    $scope.queue = {};
    $scope.selected = [];
    $scope.resses = [];

    $scope.benefactors = [];
    $scope.benefactor_selected = [];

    $scope.refreshBenefactors = function(){
        var token = sessionStorage.getItem('access_token');
        console.log('Refreshing all benefactors stuff');
        $http({
            method: 'GET',
            url: "api/donors",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            }
        }).then(function successCallback(response) {
            // Select only donors with at least 5g
            $scope.benefactors = response.data.filter(d => d.available_gold >= 5.0);
            console.log("All the benefactors:", $scope.benefactors);
        });
    };

    $scope.seatPlayer = function(s){
        seat = s+1; // provided seat is indexed from 0
        console.log("seating player in seat ", seat);
        // Post to the API to seat the player
        /// /api/characters/startplay/<int:character_id>
        var token = sessionStorage.getItem('access_token');
        character_id = $scope.selected[s].id;
        $http({
            method: 'POST',
            url: "api/characters/startplay/"+character_id,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            },
            data: {
                "seat_num": seat
            }
        }).then(function successCallback(response) {
            console.log('Successful call to /api/characters/startplay [POST]');
            $scope.refreshQueue();
        });
    };

    $scope.resPlayer = function(s){
        seat = s+1; // provided seat is indexed from 0
        console.log("Ressing player: ", seat);
        var token = sessionStorage.getItem('access_token');
        character_id = $scope.queue.playing[s].id;
        console.log('benefactor_selected[]:', $scope.benefactor_selected);
        // Post a purchase for the res
        var resdata = {
            "character_id": character_id,
            "benefactor_id": Number($scope.benefactor_selected[s])
        }
        $http({
            method: 'POST',
            url: "api/characters/res/"+character_id,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            },
            data: resdata
        }).then(function successCallback(response) {
            console.log('Successful call to /api/characters/res [POST]');
            $scope.refreshQueue();
        });
    };

    $scope.killPlayer = function(s){
        seat = s+1; // provided seat is indexed from 0
        console.log("killing player in seat ", seat);
        // Post to the API to seat the player
        var token = sessionStorage.getItem('access_token');
        character_id = $scope.queue.playing[s].id;
        $http({
            method: 'POST',
            url: "api/characters/death/"+character_id,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            },
            data: {}
        }).then(function successCallback(response) {
            console.log('Successful call to /api/characters/death [POST]');
            $scope.refreshQueue();
        });
    };

    // Setup the queue poller
    $scope.refreshQueue = function(){
        console.log('polling queue...')
        var token = sessionStorage.getItem('access_token');
        $http({
            method: 'GET',
            url: "api/queue/",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "JWT "+token
            }
        }).then(function successCallback(response) {
            console.log('Successful call to /api/queue [GET]');
            $scope.queue = response.data
        }, function errorCallback(response) {
            $scope.queue_error = "Could not fetch queue";
        });
    };

    $interval($scope.refreshQueue, 10000);
    $interval($scope.refreshBenefactors, 10000);
    
}]);


