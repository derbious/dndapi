var renderDonorViewPage;
var reorderQueue;
var removeQueue;
var unremoveCharacter;

$(function () {
  //console.log(env);
  // Perform the login form submition
  $("#loginForm").submit(function( event ) {
    //take the login and password.
    //POST to the /auth endpoint
    var d = { username: $("#usernameInput").val(),
        password: $("#passwordInput").val() }
    $.ajax({
      url: "api/auth",
      type: 'post',
      data: JSON.stringify(d),
      headers: {
        'Content-Type': 'application/json' },
      dataType: 'json',
      success: function(r) {
          console.log(r);
          sessionStorage.setItem('access_token', r['access_token']);
          $('#navLoginButton').hide().addClass('hidden');
        }
    });
    $("#loginModal").modal('hide');
    event.preventDefault();
  });

  $("#donorSearchForm").submit(function(event) {
    // pull the string from the search
    var searchstr = $('#donorSearch').val();
    var token = sessionStorage.getItem('access_token');
    // make an api call
    $.ajax({
      url: "api/search?q="+searchstr,
      type: 'get',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': "JWT " + token
      },
      success: function(data) {
        // display the results in the table
        console.log(data);
        renderDonorSearchTable(JSON.parse(data));
      },
      error: function() {
        alert('search FAIL');
      }
    });
    event.preventDefault();
  });

  // Perform the login form submition
  $("#registerDonorForm").submit(function( event ) {
    // pull the info
    event.preventDefault();
    var d = { firstname: $('#donorFirstName').val(),
              lastname: $('#donorLastName').val(),
              email: $('#donorEmail').val(),
              address: $('#donorAddress').val()
    }
    if ($('#donorDci').val() != '') {
      d.dci = $('#donorDci').val();
    }
    var token = sessionStorage.getItem('access_token');
    $.ajax({
      url: "api/donors/",
      type: 'POST',
      data: JSON.stringify(d),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': "JWT " + token
      },
      dataType: 'json',
      statusCode: {
        201: function(data) {
          console.log(data)
          $('#donorInvalidRequest').hide().addClass('invisible');
          renderDonorViewPage(data.id);
        }
      },
      error: function(e) {
          console.log(e);
          $('#donorInvalidRequest').show().removeClass('invisible');
      }
    });
  });

  // Setup the check function that periodically checks to see if
  // your credentials are still valid.
  setInterval(credCheck, 30000);
  function credCheck() {
    var token = sessionStorage.getItem('access_token');
    $.ajax({
      url: 'api/check',
      type: 'get',
      headers: {
        'Authorization': "JWT " + token
      },
      statusCode: {
        401: function() {
          //creds bad => clear token, and show the login button
          sessionStorage.removeItem('access_token');
          $('#navLoginButton').show().removeClass('invisible');
        },
        200: function() {
          $('#navLoginButton').hide().addClass('invisible');
        }
      }
    });
  }
  credCheck(); // call it right off


  //setInterval(refreshPlayerQueue, 5000);
  function refreshPlayerQueue() {
    var token = sessionStorage.getItem('access_token');
    $.ajax({
        url: "api/queue/",
        headers: {
          'Authorization': "JWT " + token
        },
        dataType: 'json',
        success: function(e){
          console.log(e);
          $('#playerQueuePage').html('<ul id="playerQueueList" class="list-group col-8"></ul>');
          for(i=0; i<e['waiting'].length; i++){
            pq_id = "pq-"+i
            idx = parseInt(i, 10)+1;
            var row = '<li class="list-group-item"><div class="container">';
            row += '<div class="row">';
            row += '<p class="col-1 h2">'+idx+'</p>';
            row += '<div class="col-1 btn-group-sm btn-group-vertical" role="group">';
            up_disabled = "";
            dn_disabled = "";
            if(i == 0){
              up_disabled = "disabled";
            }
            if(i == (e['waiting'].length - 1)){
              dn_disabled = "disabled";
            }
            var id = e['waiting'][i]['id'];
            var up_pos = i;
            var dn_pos = i+2;
            row += '  <button type="button" class="btn btn-secondary" onclick="reorderQueue('+id+','+up_pos+');" '+up_disabled+'>up</button>';
            row += '  <button type="button" class="btn btn-secondary" onclick="reorderQueue('+id+','+dn_pos+');" '+dn_disabled+'>down</button>';
            row += '</div>';
            row += '<p class="col-5 h3"><i>player:</i> '+e['waiting'][i]['player_name']+'</p>';
            row += '<p class="col-4 h3"><i>character:</i> '+e['waiting'][i]['name']+'</p>';
            row += '<button type="button" class="btn btn-primary" onclick="removeQueue('+id+');">remove</button>';
            row += '</div>';
            row += '</div></li>';

            $('#playerQueuePage').append(row);
          }
        }
    });
  }
  refreshPlayerQueue();


  reorderQueue = function(id, to_pos){
    var movedata = {
      'id': id,
      'to_pos': to_pos
    };
    var token = sessionStorage.getItem('access_token');
    //issue json call to reorder the queue
    $.ajax({
      url: "api/queue/reorder/",
      type: 'post',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': "JWT " + token
      },
      data: JSON.stringify(movedata),
      dataType: 'json',
      success: function(data) {
        console.log(data)
        refreshPlayerQueue();
      }
    });
  }


  removeQueue = function(id){
    if(confirm('Remove character from queue?')){
      var token = sessionStorage.getItem('access_token');
      //issue json call to reorder the queue
      $.ajax({
        url: "api/queue/remove/"+id,
        type: 'post',
        headers: {
          'Authorization': "JWT " + token
        },
        dataType: 'json',
        success: function(data) {
          refreshPlayerQueue();
        }
      });
    } else {
      refreshPlayerQueue();
    }
  }

  // Page switching logic
  const pages = [
    $('#searchPage'),
    $('#registerDonorPage'),
    $('#registerCharacterPage'),
    $('#playerQueuePage'),
    $('#donorViewPage'),
    $('#addDonationPage'),
    $('#addCharacterPage')
  ]

  function pagesToHide(arr, index) {
    return arr.filter(function(value, arrIndex) {
      return index !== arrIndex;
    });
  }


  $('#homeLink').click(function (){
    $.each(pagesToHide(pages, 0), function(index, value) {
      value.hide().addClass('invisible');
    });
    $('#searchPage').show().removeClass('invisible');
  });

  $('#registerDonorLink').click(function (){
    $.each(pagesToHide(pages, 1), function(index, value) {
      value.hide().addClass('invisible');
    });
    // Clear the form fields
    $('#registerDonorForm')[0].reset();
    $('#donorInvalidRequest').hide().addClass('invisible');
    $('#registerDonorPage').show().removeClass('invisible');
  });

  $('#registerCharacterLink').click(function (){
    $.each(pagesToHide(pages, 2), function(index, value) {
      value.hide().addClass('invisible');
    });
    $('#registerCharacterPage').show().removeClass('invisible');
  });

  $('#playerQueueLink').click(function (){
    $.each(pagesToHide(pages, 3), function(index, value) {
      value.hide().addClass('invisible');
    });
    $('#playerQueuePage').show().removeClass('invisible');
  });


  renderDonorViewPage = function(donor_id){
    $.each(pagesToHide(pages, 4), function(index, value) {
      value.hide().addClass('invisible');
    });
    console.log('Starting donor view render');
    //$('#donorViewPage').html('donorView: donor_id='+donor_id);
    var token = sessionStorage.getItem('access_token');
    // Grab the donor info from the web service
    var donorp = $.ajax({
        url: "api/donors/"+donor_id,
        headers: {
          'Authorization': "JWT " + token
        },
        dataType: 'json'
      });
    var donationp = $.ajax({
        url: "api/donations/?donor_id="+donor_id,
        headers: {
          'Authorization': "JWT " + token
        },
        dataType: 'json'
      });
    var characterp = $.ajax({
        url: "api/characters/?player_id="+donor_id,
        headers: {
          'Authorization': "JWT " + token
        },
        dataType: 'json'
      });
    
    $.when(donorp,donationp,characterp).done(function(donor_res,donations_res,characters_res) {
      console.log('BLARG');
      console.log('attempting to display characters', characters_res);
      var donor = donor_res[0];
      var donations = donations_res[0];
      var characters = characters_res[0];
      //console.log('attempting to display characters', characters);
      if(!donor.dci_number){
        donor.dci_number = ''
      }
      var render = '<div class="container-fluid row justify-content-center my-3">';
      render += '<div class="col-8"><h2>Donor Information</h2><table class="table">';
      render += '<tr><td>First Name</td><td>'+donor.first_name+'</td></tr>'
      render += '<tr><td>Last Name</td><td>'+donor.last_name+'</td></tr>'
      render += '<tr><td>Email Address</td><td>'+donor.email_address+'</td></tr>'
      render += '<tr><td>DCI Number</td><td>'+donor.dci_number+'</td></tr>'
      render += '</table>';
      render += '<h3>Characters</h3>';
      render += '<a id="addCharacterButton" class="btn btn-primary" href="#">Add Character</a>';
      //render out all of the characters
      if(characters.length > 0) {
        render += '<table class="table"><thead><tr><th>name</th><th>race</th><th>class</th><th>status</th>';
        for(i=0; i<characters.length; i++){
          render += '<tr><td>'+characters[i].name+'</td>';
          render += '<td>'+characters[i].race+'</td>';
          render += '<td>'+characters[i].class+'</td>';
          render += '<td>'+characters[i].state;
          // show a un-remove button if in 'canceled' state
          if(characters[i].state == 'canceled'){
            render += ' <a href="javascript:unremoveCharacter('+donor.id+','+characters[i]['id']+');">unremove</a>';
          }
          render += '</td></tr>';
        }
        render += '</table>';
      }
      render += '<h3>Donations</h3>';
      //Loop throught the donations
      console.log('attempting to display donations', donations);
      if(donations.length > 0){
        render += '<table class="table"><thead><tr><th>timestamp</th><th>amount</th><th>method</th><th>reason</th></thead></tr>';
        for(i=0; i<donations.length; i++){
          render += '<tr><td>'+donations[i].timestamp+'</td><td>'+donations[i].amount+'</td><td>'+donations[i].method+'</td><td>'+donations[i].reason+'</td></tr>';
        }
        render += '</table>';
      }
      render += '<a id="addDonationButton" class="btn btn-primary" href="#">Add Donation</a>';
      render += '</div></div>';

      $('#donorViewPage').html(render);
      $('#addDonationButton').click(function(event){
        event.preventDefault();
        renderAddDonationPage(donor.id);
      });
      $('#addCharacterButton').click(function(event){
        event.preventDefault();
        renderAddCharacterPage(donor.id);
      });


      $('#donorViewPage').show().removeClass('invisible');
    });
  }

  $('#donationForm').submit(function(event){
    event.preventDefault();
    //pull data from form, do an AJAX call
    var d = { donor_id: $('#donationDonorId').val(),
              amount: $('#donationAmount').val(),
              method: $('#donationMethod').val(),
              reason: $('#donationReason').val()
    }
    var token = sessionStorage.getItem('access_token');
    $.ajax({
      url: "api/donations/",
      type: 'post',
      data: JSON.stringify(d),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': "JWT " + token
      },
      dataType: 'json',
      success: function(data) {
          console.log(data);
          $('#donationError').hide().addClass('invisible');
          renderDonorViewPage(d.donor_id);
      },
      error: function(e) {
          $('#donationError').show().removeClass('invisible');
      }
    });
  });
  
  $('#characterForm').submit(function(event){
    event.preventDefault();
    //pull data from form, do an AJAX call
    var d = { player_id: $('#characterDonorId').val(),
              name: $('#characterName').val(),
              race: $('#characterRace').val(),
              char_class: $('#characterClass').val(),
              fee_type: $('#characterPaymentForm').val()
    }
    var token = sessionStorage.getItem('access_token');
    $.ajax({
      url: "api/characters/",
      type: 'post',
      data: JSON.stringify(d),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': "JWT " + token
      },
      dataType: 'json',
      success: function(data) {
          console.log(data);
          $('#characterError').hide().addClass('invisible');
          renderDonorViewPage(d.player_id);
      },
      error: function(e) {
          $('#characterError').show().removeClass('invisible');
      }
    });
  });

  unremoveCharacter = function(donor_id, id){
    var token = sessionStorage.getItem('access_token');
    //issue json call to unremove character
    $.ajax({
      url: "api/queue/unremove/"+id,
      type: 'post',
      headers: {
        'Authorization': "JWT " + token
      },
      dataType: 'json',
      success: function(data) {
        console.log(data);
        renderDonorViewPage(donor_id);
      }
    });
  }

  function renderAddDonationPage(donor_id){
    $.each(pages, function(index, value) {
      value.hide().addClass('invisible');
    });
    //Clear the form, then set the donor_id;
    $('#donationForm')[0].reset();
    $('#donationDonorId').val(donor_id);
    $('#addDonationPage').show().removeClass('invisible');
  }

  function renderAddCharacterPage(donor_id){
    $.each(pages, function(index, value) {
      value.hide().addClass('invisible');
    });
    //Clear the form, then set the donor_id;
    $('#characterForm')[0].reset();
    $('#characterDonorId').val(donor_id);
    $('#addCharacterPage').show().removeClass('invisible');
  }

  function renderDonorSearchTable(data) {
    render = "<div class=\"col-8\"><table class=\"table\"><thead><th>#</th><th>first name</th><th>last name</th><th>email</th></thead><tbody>";
    for(var i=0; i<data.length; i++){
      render += "<tr><td><a href=\"javascript:renderDonorViewPage("+data[i].id+");\">"+data[i].id+"</a></td><td>"+data[i].first_name+"</td><td>"+data[i].last_name+"</td><td>"+data[i].email_address+"</td></tr>";
    }
    render += "</tbody></table></div>";
    $('#searchResultTable').html(render);
  }
});
