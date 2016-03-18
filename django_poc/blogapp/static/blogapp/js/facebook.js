window.fbAsyncInit = function () {
  FB.init({
      appId:'488339124689695',
      oauth:true,
      status:true, // check login status
      cookie:true, // enable cookies to allow the server to access the session
      xfbml:true // parse XFBML
  });
};

function fb_login(strLoginId) {
  	FB.getLoginStatus(function (response) {
      	if (response.status === 'connected') {
        	fb_logout(strLoginId);
      	} else {
          	FB.login(function (response) {
              	if (response.authResponse) {
	                access_token = response.authResponse.accessToken; //get access token
	                user_id = response.authResponse.userID; //get FB UID
	                // fnViewFacebookPageList(access_token);
	                console.log('Welcome!!! Fetching your information ...'+access_token);
	                console.log(response.authResponse.name);
	                console.log(user_id);

                  	FB.api('/me', function(response) {
                  		alert(access_token);
                  		if (access_token) {
                  			$.ajax({
                  				url: '/facebook-login/',
                  				method: 'post',
                  				data: response,
                  				success: function(data) {
                  					alert(data);
                  					window.location.href = '/home'
                  				} 
                  			});
                  		}
	                	console.log('Good to see you, ' + response.name + '.');
	                   	console.log(response.id);
                	});
              		}
	        	}, {scope:'public_profile,email'});
    	}
	})//end
}

// fb-logout
function fb_logout(strLoginId) {
  FB.logout(function (response) {
      // FB.Auth.setAuthResponse(null, 'unknown');
      fb_login(strLoginId);
  });
}// FB.log-out