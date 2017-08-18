"use strict"

$(document).ready(function(){

  // if ($("#logout-button").prop("hidden") === false ) {
  //     $("#when-loggedin").show();
  // }

//Execute login
//event listener
  $("#login-link").click(function(evt) {
    $("#login-modal").modal("show");
  });
//event listener to submit login form
$("#loginmodal-submit").click(doLogin);

  // event handler function
  function doLogin(evt) {
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
                //hide login modal
                $("#login-modal").modal("hide");
                //change message to show logged in status
                //change home page to show saved paws and search shelters
                
                $("#logout-button").removeClass("hidden");
                $("#logout-button").show();
                $("#login-button").hide(); 
                $("#when-loggedin").show();  
                $("#logout-message").hide(); 
                $("#saved-paws-link").show();
                $("#search-shelters-link").show(); 
                // window.location.reload();
                $("#welcome-message").text("Welcome, " + results.firstname + "!");
                $("#welcome-message").show();  
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

      //make the AJAX request
      $.get("/logout.json", function(results){
            console.log("results: ", results);
            var success = results.success;
            
            if (success === true) {
                //change message to show logged out status
                console.log(results.message);
                $("#welcome-message").hide();
                $("#logout-message").show();
                $("#when-loggedin").hide();
                $("#logout-button").hide();
                $("#login-button").removeClass("hidden");
                $("#login-button").show();
                $("#saved-paws-link").hide();
                $("#search-shelters-link").hide();
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

//Show registration modal
//event listener 
  $("#register-link").on("click", function(){
    $("#register-modal").modal("show");
  }); 

  

 });//end of document ready function