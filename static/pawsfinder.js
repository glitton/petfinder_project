"use strict"

$(document).ready(function(){
  // Show this alert for the first time only
    $('.alert-message').one('click', function () {
      alert("This app is still a work in progress.\n To use this app without registering, enter the following:\n username:admin@gmail.com password: admin123.\n Or feel free to register for an account. Happy PAWS Finding ;-)");
    });            
  // var alerted = localStorage.getItem('alerted') || '';
  //   if (alerted != 'yes') {
  //      alert('This app is still a work in progress and I know that this pop-up window appears when the page refreshes.\n To use this app without registering, enter the following details:\n username:admin@gmail.com password: admin123.\n Otherwise feel free to register for an account. Happy PAWS hunting ;-)');
  //    localStorage.setItem('alerted','yes');
  //   }

  // When user is logged in, show the complete form
  if ($("#logout-button").prop("hidden") === false ) {
      $("#when-loggedin").show(); 
  }

//Execute login 
  // This is the event listener
  $("#login-link").click(function(evt) {
    $("#login-modal").modal("show");
  });
//event listener to submit login form
$("#loginmodal-submit").click(doLogin);

  // event handler function
  function doLogin(evt) {
    evt.preventDefault();
      //get the form values
      var email = $("#login-email-field").val();
      var password = $("#login-password-field").val();

      //pack up the form values into an object
      var loginData = {"email": email,
                      "password": password};
      console.log(loginData);                

      //make the AJAX request
      $.post("/login.json", loginData, function(results){
            console.log("results: ", results);
            var success = results.success;
            
            if (success === true) {
                
                $("#login-message").removeClass("hidden").addClass("show");
                // hide login modal
                $("#login-modal").modal("hide");
                window.location.reload(true);
                //change message to show logged in status
                //change home page to show saved paws and search shelters
                //change home page to show expanded form
                $("#when-loggedin").show();
                $("#logout-button").removeClass("hidden");
                $("#logout-button").show();
                $("#login-button").hide();   
                $("#saved-paws-link").show();
                $("#search-shelters-link").show(); 

                
                // $("#logout-message").addClass("hidden"); 
                // $("#welcome-message").text("Welcome, " + results.firstname + "!");
                  
                // $("#welcome-message").removeClass("hidden").addClass("show");
                
            }
            else {    
                $("#login-error-message").html(results.message);
                $("#login-error-message").show(); 
            }
        } //end of callback function
      ); //end of AJAX request
}; //end of doLogin function


//Execute logout
//event listener to execute logout
$("#logout-link").click(doLogout);
  //event handler
  function doLogout(evt) {
    evt.preventDefault()
      //make the AJAX request
      $.post("/logout.json", function(results){
            console.log("results: ", results);
            var success = results.success;
            
            if (success === true) {
                //change message to show logged out status
                console.log(results.message);
                $("#welcome-message").hide();
                $("#when-loggedin").hide();
                $("#logout-button").hide();
                $("#login-button").removeClass("hidden");
                $("#login-button").show();
                $("#saved-paws-link").hide();
                $("#search-shelters-link").hide();
                $("#logout-message").removeClass("hidden").addClass("show");
            }
        } //end of callback function
      ); //end of AJAX request
  }; //end of logout function

//Hide or show the breeds dropdown menu
    $("#cats").hide(); // hide this when the page loads
  $("#animal-type").on("change", function() {
        if ($("#animal-type").find(":selected").text() !== "dog") {
              $("#dogs").hide();
              $("#cats").show();
      } else {
              $("#cats").hide();
              $("#dogs").show();
      }
  });   


 });//end of document ready function