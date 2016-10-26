var auth2;

function signInCallback(authResult) {
  if (authResult['code']) {
    $('#sign-in-button').attr('style', 'display: none');
    var state = $('input[type="hidden"]').attr('value');

    $.ajax({
      type: 'POST',
      url: '/storeauthcode?state=' + state,
      contentType: 'application/octet-stream; charset=utf-8',
      processData: false,
      data: authResult['code'],
      success: function(result) {
        $('#result').html('Logging you in...');
        $('#login-logout').html('<a href="/logout">Logout</a>')
        setTimeout(function() {
          window.location.href = '/';
        }, 2000);
      }
    });
  }
}

function start() {
  gapi.load('auth2', function() {
    auth2 = gapi.auth2.init({
      client_id: '838200058961-rm8trg3bvqa1m8es5r1fsjt0n26v7um4.apps.googleusercontent.com',
    });
  });
}

$(window).on('load', function() {
  start();
  $('#sign-in-button').click(function() {
    auth2.grantOfflineAccess({'redirect_uri': 'postmessage'}).then(signInCallback);
  });
});
