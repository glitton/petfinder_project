"use strict"

$(document).ready(function(){


//Show registration modal
  $("#register-link").on("click", function(){
    $("#register-modal").modal("show");
  }); 

  // Confirm Password function, makes sure that both passwords
  // match before users submits
   $("#confirm-password").keyup(function(){

    //Store the password field inputs into variables
    var password1 = document.getElementById('password-field');
    var password2 = document.getElementById('confirm-password');
    //Store the confimation message in a variable
    var message = document.getElementById('confirm-message');
    //Set the colors to indicate whether password matched or not
    var goodPassword = "#66cc66";
    var badPassword = "#ff6666";
    //Compare the values in the password and the confirm password fields
    if(password1.value === password2.value){
        //The passwords match. 
        //Set the color to the good color and a confirm message
        password2.style.backgroundColor = goodPassword;
        message.style.color = goodPassword;
        message.innerHTML = "&#10004"; 
        document.getElementById("signup-btn").disabled = false;
        // $('.btn').prop('disabled', false); jQuery version
      } 
    
    else {
        //The passwords do not match.
        //Set the color to the bad color and notify the user.
        password2.style.backgroundColor = badPassword;
        message.style.color = badPassword;
        message.innerHTML = "&#10060";
        document.getElementById("signup-btn").disabled = true;
        // $('.btn').prop('disabled', true); jQuery version
    }
  });  

  // When reset btn in signup form is clicked, form should have no colors
  $('#cancel-signup').click(function(){
    var message = document.getElementById('confirm-message');
    var pass2Color = document.getElementById('inputPass2');
    pass2Color.style.backgroundColor = '#ffffff';
    message.style.visibility = 'hidden';
  });


 });//end of document ready function